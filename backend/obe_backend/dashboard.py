from django.db.models import Avg, Count, Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from attainments.models import Attainment
from courses.models import Course
from projects.models import Project


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        courses = Course.objects.all()
        if request.user.is_faculty_role:
            courses = courses.filter(faculty=request.user)

        courses = courses.annotate(
            outcome_count=Count('outcomes', distinct=True),
            attainment_count=Count(
                'attainments',
                filter=Q(attainments__final_attainment__isnull=False),
                distinct=True,
            ),
            avg_final=Avg('attainments__final_attainment'),
            avg_level=Avg('attainments__attainment_level'),
            project_total=Count('projects', distinct=True),
            projects_active=Count(
                'projects',
                filter=Q(projects__evaluation_status__in=['NOT_STARTED', 'IN_PROGRESS']),
                distinct=True,
            ),
        ).order_by('-academic_year', 'course_code')

        course_rows = list(courses)
        course_ids = [c.id for c in course_rows]

        pending = sum(
            1 for c in course_rows
            if c.outcome_count > 0 and c.attainment_count < c.outcome_count
        )

        attainments = Attainment.objects.filter(course_id__in=course_ids)
        overall_avg = attainments.aggregate(avg=Avg('final_attainment'))['avg']

        level_distribution = {str(i): 0 for i in range(4)}
        for row in attainments.exclude(attainment_level__isnull=True).values('attainment_level').annotate(n=Count('id')):
            level_distribution[str(row['attainment_level'])] = row['n']

        projects = Project.objects.filter(course_id__in=course_ids)
        status_counts = {key: 0 for key, _ in Project.Status.choices}
        for row in projects.values('evaluation_status').annotate(n=Count('id')):
            status_counts[row['evaluation_status']] = row['n']

        return Response({
            'course_count': len(course_rows),
            'outcome_count': sum(c.outcome_count for c in course_rows),
            'pending_attainment': pending,
            'average_final_attainment': round(float(overall_avg), 2) if overall_avg is not None else None,
            'level_distribution': level_distribution,
            'projects': {
                'total': projects.count(),
                'not_started': status_counts['NOT_STARTED'],
                'in_progress': status_counts['IN_PROGRESS'],
                'evaluated': status_counts['EVALUATED'],
                'active': status_counts['NOT_STARTED'] + status_counts['IN_PROGRESS'],
            },
            'courses': [
                {
                    'id': c.id,
                    'course_code': c.course_code,
                    'course_name': c.course_name,
                    'semester': c.semester,
                    'academic_year': c.academic_year,
                    'outcome_count': c.outcome_count,
                    'attainment_count': c.attainment_count,
                    'avg_final': round(float(c.avg_final), 2) if c.avg_final is not None else None,
                    'avg_level': round(float(c.avg_level), 2) if c.avg_level is not None else None,
                    'project_total': c.project_total,
                    'projects_active': c.projects_active,
                    'pending': c.outcome_count > 0 and c.attainment_count < c.outcome_count,
                }
                for c in course_rows
            ],
        })
