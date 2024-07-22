from flask import make_response, Blueprint

import spider
from spider.job.bilibil_tsak import BiliBiliTask

bp = Blueprint('bilibili', __name__)


@bp.get("/init/index")
def init_index():
    # 获取预期运行的列表
    bilibil_tsak = BiliBiliTask()
    spider.common_executor.submit(bilibil_tsak.season_index_result_task)
    return make_response('ok')


@bp.get("/init/condition")
def init_condition():
    # 获取预期运行的列表
    bilibil_tsak = BiliBiliTask()
    spider.common_executor.submit(bilibil_tsak.season_index_condition_task)
    return make_response('ok')


@bp.get("/init/details")
def init_details():
    # 获取预期运行的列表
    bilibil_tsak = BiliBiliTask()
    spider.common_executor.submit(bilibil_tsak.season_details_task)
    return make_response('ok')
