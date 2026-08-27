def faculty_owns_course(user, course):
    if user is None or course is None:
        return False
    if getattr(user, 'is_faculty_role', False):
        return course.faculty_id == user.id
    return True


def owned_course_or_error(user, course, error_cls):
    if not faculty_owns_course(user, course):
        raise error_cls('You can only use your own course offerings.')
    return course
