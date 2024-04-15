import frappe
from erpnext.projects.doctype.project.project import Project
from frappe.utils import add_days, flt, get_datetime, get_time, get_url, nowtime, today
from frappe.desk.form import assign_to


class CustomProject(Project):
    def validate(self):
        if not self.is_new():
            self.copy_from_template()

    def copy_from_template(self):
        """
        Copy tasks from template
        """
        if self.project_template and not frappe.db.get_all(
            "Task", dict(project=self.name), limit=1
        ):

            # has a template, and no loaded tasks, so lets create
            if not self.expected_start_date:
                # project starts today
                self.expected_start_date = today()

            template = frappe.get_doc("Project Template", self.project_template)

            if not self.project_type:
                self.project_type = template.project_type

            # create tasks from template
            project_tasks = []
            tmp_task_details = []
            for task in template.tasks:
                template_task_details = frappe.get_doc("Task", task.task)
                tmp_task_details.append(template_task_details)
                task = self.create_task_from_template(template_task_details)
                project_tasks.append(task)

            self.dependency_mapping(tmp_task_details, project_tasks)

    def create_task_from_template(self, task_details):

        if self.project_template:

            task = frappe.get_doc(
                dict(
                    doctype="Task",
                    subject=task_details.subject,
                    project=self.name,
                    status="Open",
                    exp_start_date=self.calculate_start_date(task_details),
                    exp_end_date=self.calculate_end_date(task_details),
                    description=task_details.description,
                    task_weight=task_details.task_weight,
                    type=task_details.type,
                    issue=task_details.issue,
                    is_group=task_details.is_group,
                    color=task_details.color,
                    template_task=task_details.name,
                )
            ).insert()

            project_template = frappe.get_doc("Project Template", self.project_template)

            for task_tem in project_template.tasks:

                args = {
                    "assign_to": [task_tem.user],
                    "doctype": "Task",
                    "name": task.name,
                    "description": " task.subject",
                    "notify": 1,
                }
                assign_to.add(args)

            return task
        else:
            return frappe.get_doc(
                dict(
                    doctype="Task",
                    subject=task_details.subject,
                    project=self.name,
                    status="Open",
                    exp_start_date=self.calculate_start_date(task_details),
                    exp_end_date=self.calculate_end_date(task_details),
                    description=task_details.description,
                    task_weight=task_details.task_weight,
                    type=task_details.type,
                    issue=task_details.issue,
                    is_group=task_details.is_group,
                    color=task_details.color,
                    template_task=task_details.name,
                )
            ).insert()
