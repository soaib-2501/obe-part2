from django.db import transaction
from django.db.models import Avg
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from courses.models import Course
from .defaults import ensure_sheet_blocks
from .models import Assessment, Student, StudentMark, GradeBand
from .serializers import (
    AssessmentSerializer, StudentSerializer, StudentMarkSerializer, GradeBandSerializer,
)


def faculty_scope(user, qs, lookup='course__faculty'):
    if user.is_faculty_role:
        return qs.filter(**{lookup: user})
    return qs


class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all().prefetch_related('questions')
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        qs = faculty_scope(self.request.user, super().get_queryset())
        course_id = self.request.query_params.get('course')
        return qs.filter(course_id=course_id) if course_id else qs

    @action(detail=False, methods=['post'])
    def ensure(self, request):
        """Create T1/T2/T3/TA/Feedback blocks + default questions + grade bands if missing."""
        course_id = request.data.get('course')
        if not course_id:
            return Response({'error': 'course is required'}, status=400)
        course = Course.objects.filter(pk=course_id).first()
        if not course:
            return Response({'error': 'Course not found.'}, status=404)
        if request.user.is_faculty_role and course.faculty_id != request.user.id:
            return Response({'error': 'Not allowed.'}, status=403)
        created = ensure_sheet_blocks(course)
        assessments = Assessment.objects.filter(course=course, assessment_type__in=['T1', 'T2', 'T3', 'TA', 'FEEDBACK'])
        return Response({
            'created': created,
            'assessments': AssessmentSerializer(assessments, many=True).data,
        })

    @action(detail=False, methods=['get'])
    def report(self, request):
        course_id = request.query_params.get('course')
        if not course_id:
            return Response({'error': 'course is required'}, status=400)
        assessments = faculty_scope(request.user, Assessment.objects.filter(course_id=course_id))
        rows = []
        for assessment in assessments:
            marks = StudentMark.objects.filter(assessment=assessment)
            overall = marks.aggregate(avg=Avg('marks_obtained'))['avg']
            by_co = []
            for item in marks.values('course_outcome', 'course_outcome__co_code').annotate(avg=Avg('marks_obtained')):
                by_co.append({
                    'course_outcome': item['course_outcome'],
                    'co_code': item['course_outcome__co_code'],
                    'average': round(float(item['avg']), 2) if item['avg'] is not None else None,
                })
            rows.append({
                'id': assessment.id,
                'assessment_type': assessment.assessment_type,
                'max_marks': assessment.max_marks,
                'class_average': round(float(overall), 2) if overall is not None else None,
                'entry_count': marks.count(),
                'by_co': by_co,
            })
        return Response({
            'course': int(course_id),
            'student_count': faculty_scope(request.user, Student.objects.filter(course_id=course_id)).count(),
            'assessments': rows,
        })


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        qs = faculty_scope(self.request.user, super().get_queryset())
        course_id = self.request.query_params.get('course')
        return qs.filter(course_id=course_id).order_by('roll_number') if course_id else qs.order_by('roll_number')


class StudentMarkViewSet(viewsets.ModelViewSet):
    queryset = StudentMark.objects.all()
    serializer_class = StudentMarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        qs = faculty_scope(self.request.user, super().get_queryset(), 'assessment__course__faculty')
        assessment_id = self.request.query_params.get('assessment')
        return qs.filter(assessment_id=assessment_id) if assessment_id else qs

    @action(detail=False, methods=['post'])
    def replace(self, request):
        """Replace all marks for one assessment in one transaction (fast path for the grid)."""
        assessment_id = request.data.get('assessment')
        raw_marks = request.data.get('marks') or []
        if not assessment_id:
            return Response({'error': 'assessment is required'}, status=400)
        assessment = faculty_scope(
            request.user,
            Assessment.objects.select_related('course'),
        ).filter(pk=assessment_id).first()
        if not assessment:
            return Response({'error': 'Assessment not found.'}, status=404)
        questions = {q.id: q for q in assessment.questions.all()}
        student_ids = set(
            Student.objects.filter(course_id=assessment.course_id).values_list('id', flat=True)
        )
        objs = []
        for row in raw_marks:
            try:
                sid = int(row.get('student'))
                qid = int(row.get('question'))
                val = row.get('marks_obtained')
            except (TypeError, ValueError):
                continue
            if sid not in student_ids or qid not in questions:
                continue
            if val is None or val == '':
                continue
            try:
                num = float(val)
            except (TypeError, ValueError):
                continue
            q = questions[qid]
            objs.append(StudentMark(
                assessment=assessment,
                student_id=sid,
                question_id=qid,
                course_outcome_id=q.course_outcome_id,
                marks_obtained=num,
            ))
        with transaction.atomic():
            StudentMark.objects.filter(assessment=assessment).delete()
            if objs:
                StudentMark.objects.bulk_create(objs, batch_size=200)
            roster_n = Student.objects.filter(course_id=assessment.course_id).count()
            assessment.total_students = roster_n
            assessment.appeared = len({o.student_id for o in objs})
            assessment.save(update_fields=['total_students', 'appeared'])
        return Response({
            'saved': len(objs),
            'total_students': assessment.total_students,
            'appeared': assessment.appeared,
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            saved = self._upsert_marks(serializer.validated_data)
            return Response(StudentMarkSerializer(saved, many=True).data, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)

    def _upsert_marks(self, rows):
        saved = []
        with transaction.atomic():
            for row in rows:
                question = row.get('question')
                defaults = {
                    'marks_obtained': row.get('marks_obtained'),
                    'course_outcome': row.get('course_outcome') or (question.course_outcome if question else None),
                }
                obj, _ = StudentMark.objects.update_or_create(
                    assessment=row['assessment'],
                    student=row['student'],
                    question=question,
                    defaults=defaults,
                )
                saved.append(obj)
        return saved


class GradeBandViewSet(viewsets.ModelViewSet):
    queryset = GradeBand.objects.all()
    serializer_class = GradeBandSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        qs = faculty_scope(self.request.user, super().get_queryset())
        course_id = self.request.query_params.get('course')
        return qs.filter(course_id=course_id) if course_id else qs
