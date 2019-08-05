from .exceptions import ProjectReferenceNotDefinedException


class ProjectReference:
    def __init__(self, project_id=None, location=None):
        self._project_id = project_id
        self._location = location

    @property
    def project_id(self):
        if not self._project_id:
            raise ProjectReferenceNotDefinedException()
        return self._project_id

    @project_id.setter
    def project_id(self, project_id):
        self._project_id = project_id

    @property
    def location(self):
        if not self._location:
            raise ProjectReferenceNotDefinedException()
        return self._location

    @location.setter
    def location(self, location):
        self._location = location
