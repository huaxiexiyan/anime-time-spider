from flask import make_response, Blueprint

from spider import common_executor
from spider.job.bilibil_tsak import BiliBiliTask

bp = Blueprint('bilibili', __name__)


@bp.get("/init/index")
async def init_index():
    # 获取预期运行的列表
    bilibil_tsak = BiliBiliTask()
    common_executor.submit(bilibil_tsak.season_index_result_task)
    return make_response('ok')


@bp.get("/init/condition")
async def init_condition():
    # 获取预期运行的列表
    bilibil_tsak = BiliBiliTask()
    common_executor.submit(bilibil_tsak.season_index_condition_task)
    return make_response('ok')


@bp.get("/init/details")
async def init_details():
    # 获取预期运行的列表
    bilibil_tsak = BiliBiliTask()
    common_executor.submit(bilibil_tsak.season_details_task)
    return make_response('ok')
