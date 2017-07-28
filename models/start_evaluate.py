# -*- coding: utf-8 -*-

from odoo import api, models, fields
from datetime import datetime
import time


class EmployeeStartEvaluate(models.Model):
    _name = "employee.start.survey"
    _rec_name = "title"

    title = fields.Many2one("survey.survey", string=u"标题", required=True)
    start_date = date = fields.Date(string=u"开始日期", default=fields.Date.context_today, required=True)
    end_date = fields.Date(string=u"结束日期", required=True)
    passive_evaluate_line = fields.One2many("employee.passive.survey", "passive_evaluate_id",
                                            string=u"Passive Evaluate Line", required=True, ondelete="set null")
    evaluate_line = fields.One2many("employee.survey", "evaluate_id", string=u"Evaluate Line", required=True,
                                    ondelete="set null")
    is_end = fields.Boolean(string=u"是否结束", default=False)
    complete = fields.Boolean(string=u"是否结束", compute="_compute_complete", default=False)

    @api.multi
    def _compute_complete(self):
        """
            计算是否到了结束时间
            :return: True:  已结束，评价界面的 Button 不可点击
                     False: 未结束，评价界面的 Button 可以点击
        """
        for record in self:
            current_date = datetime.now()
            end = time.strptime(record.end_date, "%Y-%m-%d")
            time_stamp = int(time.mktime(end)) + 24 * 60 * 60
            date_array = datetime.fromtimestamp(time_stamp)
            if current_date > date_array:
                record.complete = True
                record.write({"is_end": True})

    @api.multi
    def action_print(self):
        """
            打印报表
        """
        return self.env["report"].get_action(self, "evaluate.report_evaluate_view")


class EmployeePassiveSurvey(models.Model):
    _name = "employee.passive.survey"
    _rec_name = "passive_survey"

    passive_evaluate_id = fields.Many2one("employee.start.survey", string=u"Passive Survey Id")
    passive_survey = fields.Many2one("hr.employee", string=u"被评价人", required=True)
    survey_title = fields.Char(string=u"评价标题", related="passive_evaluate_id.title.title", store=True)
    state = fields.Boolean(string=u"评价是否结束", related="passive_evaluate_id.complete")
    complete = fields.Boolean(string=u"是否完成", default=False, compute="_get_complete")
    score = fields.Float(string=u"平均得分", digits=(5, 1))
    average_score = fields.Float(string=u"平均得分", digits=(5, 1), compute="_average_score")

    @api.multi
    def action_survey_survey(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': "Results of the Survey",
            'target': 'self',
            'url': "/survey/start/" + str(self.passive_evaluate_id.title.id) + "/phantom/" + str(self.id)
        }

    @api.multi
    def _get_complete(self):
        """
            是否完成对某个人的评价
                1.) 筛选已经过期的答案记录
                2.) 如果被评价人的姓名在被评价人列表里
                3.) 如果答案记录里的评价标题等于用户显示的评价标题
                4.) 如果当前用户等于评价人
                5.) 如果答案记录里的发起评价的 id 等于发起评价的 id
                6.) 将 complete 设置为 True
            :return: True:  已完成，Button 不可点击
                     False: 未完成，Button 可以点击
        """
        user_input = self.env['survey.user_input'].search([('expire', '=', False)])
        for record in user_input:
            for line in self:
                if record.passive_name == line.passive_survey.name_related:
                    if record.survey_id == line.passive_evaluate_id.title:
                        if self.env.user == record.evaluate_name:
                            if record.start_survey_id == line.passive_evaluate_id.id:
                                line.complete = True

    @api.depends("complete")
    def _average_score(self):
        user_input = self.env["survey.user_input"].search([])
        for record in self:
            total_score = 0
            count = 0
            for user_line in user_input:
                if user_line.start_survey_id == record.passive_evaluate_id.id:
                    if user_line.passive_name == record.passive_survey.name_related:
                        total_score += user_line.score
                        count += 1
                        record.write({"score": total_score / count})


class EmployeeSurvey(models.Model):
    _name = "employee.survey"

    evaluate_id = fields.Many2one("employee.start.survey", string=u"Survey Id")
    survey_people = fields.Many2one("hr.employee", string=u"参与评价人", required=True)
