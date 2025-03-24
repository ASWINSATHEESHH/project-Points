# -*- coding: utf-8 -*-
from urllib3.util import current_time

from odoo import models, fields, api


class project_tasks(models.Model):
    _inherit = 'project.task'

    @api.onchange('stage_id')
    def point_setting(self):

        current_time = fields.Datetime.now().date()
        date_diff = 0
        if self.date_deadline:
            date_diff = (self.date_deadline - current_time).days

        base_points = 1
        if date_diff >= 0:
            dynamic_points = base_points + (0.1 * date_diff)
        else:
            dynamic_points = base_points - (0.1 * abs(date_diff))

        tasks = self.env['project.task'].search([('name', '=', self.name)])
        employees = self.env['hr.employee'].sudo().search([('user_id', 'in', tasks.user_ids.ids)])
        for employee in employees:
            if employee and self.stage_id.name == "Done":
                current_point = employee.points
                point = current_point + dynamic_points
                employee.write({'points': point})

        if self.stage_id.name == "Done":
            print(self.project_id.id)

            project_points = self.env['project.points'].search([
                ('project_id', '=', self.project_id.id)
            ])

            print(project_points.ids)

            task_details = self.env['project.task.detail'].search([
                ('task_id', '=', tasks.id),
                ('project_points_id', 'in', project_points.ids)
            ])

            print(task_details.mapped('task_id.id'))

            # Inline for loop to update project_points if conditions are met
            [pp.write({'points': dynamic_points}) for pp in project_points if
             task_details.filtered(lambda td: td.task_id.id)]

            # Create new project points and task details if necessary
            if not project_points or not task_details:
                project_points = self.env['project.points'].create({
                    'project_id': self.project_id.id,
                    'users_ids': [(6, 0, self.user_ids.ids)],
                    'points': dynamic_points,
                })

                self.env['project.task.detail'].create({
                    'project_points_id': project_points.id,
                    'task_id': tasks.id,
                    'finished_date': current_time,
                    'task_deadline': self.date_deadline,
                })


class project_points(models.Model):
    _name = 'project.points'
    _rec_name = "project_id"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    project_id = fields.Many2one('project.project','Project Name')
    users_ids = fields.Many2many('res.users')
    points = fields.Float('Points')

    tasks_ids = fields.One2many('project.task.detail','project_points_id','task')


class project_tasks(models.Model):
    _name = 'project.task.detail'

    project_points_id = fields.Many2one('project.points')
    task_id = fields.Many2one('project.task', 'project task')
    finished_date = fields.Datetime('Finished Date')
    task_deadline = fields.Datetime('Task Deadline')