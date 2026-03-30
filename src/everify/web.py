#!/usr/bin/env python3
"""
Everify Flask 应用 - 网页核查自动化系统
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from everify.core.services.template_manager import TemplateManager
from everify.core.services.entity_manager import EntityManager
from everify.core.utils.config import AppConfig
from everify.core.utils import logger
from pathlib import Path

app = Flask(__name__,
            template_folder=str(Path(__file__).parent.parent.parent / 'web' / 'templates'),
            static_folder=str(Path(__file__).parent.parent.parent / 'web' / 'static'))
app.secret_key = 'everify_flask_app_secret_key_12345'

# 初始化项目组件
tm = TemplateManager()
em = EntityManager()
config = AppConfig()


@app.route('/')
def index():
    """首页 - 重定向到诚信核查"""
    return redirect(url_for('integrity_check'))


@app.route('/integrity-check')
def integrity_check():
    """诚信核查页面"""
    # 获取进度步骤
    step = request.args.get('step', '1')
    current_step = int(step) if step.isdigit() and 1 <= int(step) <= 5 else 1

    # 加载所有模板（不分类）
    templates = tm.load_templates()

    # 获取已保存的数据
    entities = session.get('entities', [])
    selected_templates = session.get('selected_templates', [])

    # 获取模板详细信息
    selected_template_info = []
    for template_id in selected_templates:
        if template_id in templates:
            selected_template_info.append(templates[template_id])

    # 获取报告路径
    report_paths = session.get('report_paths', {})

    # 获取当前时间
    from datetime import datetime
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return render_template('integrity_check.html',
                         current_step=current_step,
                         templates=templates,
                         entities=entities,
                         selected_templates=selected_template_info,
                         active_tab='integrity_check',
                         report_paths=report_paths,
                         current_time=current_time)


@app.route('/bribery-check')
def bribery_check():
    """涉贿核查页面"""
    # 获取进度步骤
    step = request.args.get('step', '1')
    current_step = int(step) if step.isdigit() and 1 <= int(step) <= 2 else 1

    # 获取已保存的数据
    entities = session.get('entities', [])

    # 获取报告路径
    report_paths = session.get('report_paths', {})

    # 获取当前时间
    from datetime import datetime
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return render_template('bribery_check.html',
                         current_step=current_step,
                         entities=entities,
                         active_tab='bribery_check',
                         report_paths=report_paths,
                         current_time=current_time)


@app.route('/entities', methods=['GET', 'POST'])
def entities():
    """主体输入页面 - 重定向到诚信核查页面"""
    if request.method == 'POST':
        entities = request.form.get('entities', '').strip()
        if entities:
            entity_list = [e.strip() for e in entities.split('\n') if e.strip()]
            validated_entities = em.validate_entities(entity_list)
            session['entities'] = validated_entities
            return jsonify({'status': 'success', 'count': len(validated_entities)})
        else:
            return jsonify({'status': 'error', 'message': '请输入需要核查的主体'})

    # 重定向到诚信核查页面（步骤1）
    return redirect(url_for('integrity_check', step='1'))


@app.route('/templates')
def templates():
    """网页选择页面 - 重定向到诚信核查页面"""
    return redirect(url_for('integrity_check', step='2'))


@app.route('/templates/select', methods=['POST'])
def select_templates():
    """选择模板"""
    selected = request.json.get('selected', [])
    session['selected_templates'] = selected
    return jsonify({'status': 'success', 'count': len(selected)})


@app.route('/verify')
def verify():
    """执行核查页面 - 重定向到诚信核查页面"""
    return redirect(url_for('integrity_check', step='3'))


@app.route('/results')
def results():
    """结果展示页面 - 重定向到诚信核查页面"""
    return redirect(url_for('integrity_check', step='4'))


@app.route('/search')
def search():
    """搜索引擎查询页面"""
    return redirect(url_for('integrity_check', step='1'))


@app.route('/admin/templates')
def admin_templates():
    """模板管理页面"""
    templates = tm.load_templates()
    categories = tm.get_all_categories()

    # 按分类组织模板
    category_info = {}
    for category in categories:
        category_templates = tm.get_templates_by_category(category)
        category_info[category] = {
            'display_name': tm.get_category_display_name(category),
            'templates': list(category_templates.values())
        }

    return render_template('admin_templates.html',
                         templates=templates,
                         category_info=category_info,
                         user_templates_file=tm.user_templates_file)


@app.route('/api/templates')
def get_templates():
    """API: 获取所有模板信息"""
    templates = tm.load_templates()
    template_list = []

    for name, template in templates.items():
        template_list.append({
            'id': name,
            'name': template.description,
            'category': template.category,
            'category_name': tm.get_category_display_name(template.category),
            'url': template.url_pattern
        })

    return jsonify(template_list)


@app.route('/api/entities/validate', methods=['POST'])
def validate_entities():
    """API: 验证主体列表"""
    entities = request.json.get('entities', [])
    if not entities:
        return jsonify({'status': 'error', 'message': '主体列表不能为空'})

    validated = em.validate_entities(entities)
    return jsonify({
        'status': 'success',
        'count': len(validated),
        'entities': validated
    })


@app.route('/api/entities/save', methods=['POST'])
def save_entities():
    """API: 保存主体列表到会话"""
    entities = request.json.get('entities', [])
    session['entities'] = entities
    return jsonify({'status': 'success', 'count': len(entities)})


@app.route('/api/templates/info/<template_id>')
def get_template_info(template_id):
    """API: 获取单个模板信息"""
    templates = tm.load_templates()
    if template_id in templates:
        template = templates[template_id]
        return jsonify({
            'id': template_id,
            'name': template.description,
            'category': template.category,
            'category_name': tm.get_category_display_name(template.category),
            'url': template.url_pattern,
            'description': template.description
        })
    else:
        return jsonify({'status': 'error', 'message': '模板不存在'})


@app.route('/api/templates/categories')
def get_categories():
    """API: 获取模板分类信息"""
    categories = tm.get_all_categories()
    category_info = []

    for category in categories:
        count = len(tm.get_templates_by_category(category))
        category_info.append({
            'name': category,
            'display_name': tm.get_category_display_name(category),
            'count': count
        })

    return jsonify(category_info)


@app.route('/api/templates/user', methods=['POST'])
def add_user_template():
    """API: 添加用户自定义模板"""
    try:
        data = request.json
        name = data.get('name')
        description = data.get('description')
        url_pattern = data.get('url_pattern')
        category = data.get('category', 'custom')

        if not all([name, description, url_pattern]):
            return jsonify({'status': 'error', 'message': '模板名称、描述和URL模式不能为空'})

        # 验证URL模式是否包含占位符
        if '{}' not in url_pattern:
            return jsonify({'status': 'error', 'message': 'URL模式必须包含 {} 作为主体名称的占位符'})

        from everify.core.utils.config import VerifyTemplate
        # 插入上下文默认使用模板名称（英文）
        insert_context = data.get('InsertContext', name)
        template = VerifyTemplate(
            name=name,
            description=description,
            url_pattern=url_pattern,
            category=category,
            InsertContext=insert_context
        )

        if tm.save_user_template(name, template):
            return jsonify({'status': 'success', 'message': '模板添加成功'})
        else:
            return jsonify({'status': 'error', 'message': '模板添加失败'})
    except Exception as e:
        logger.error(f"添加用户模板失败: {e}")
        return jsonify({'status': 'error', 'message': f'模板添加失败: {str(e)}'})


@app.route('/api/templates/user/<name>', methods=['PUT'])
def update_user_template(name):
    """API: 更新用户自定义模板"""
    try:
        data = request.json
        description = data.get('description')
        url_pattern = data.get('url_pattern')
        category = data.get('category', 'custom')

        from everify.core.utils.config import VerifyTemplate
        # 插入上下文默认使用模板名称（英文）
        insert_context = data.get('InsertContext', name)
        template = VerifyTemplate(
            name=name,
            description=description,
            url_pattern=url_pattern,
            category=category,
            InsertContext=insert_context
        )

        if tm.save_user_template(name, template):
            return jsonify({'status': 'success', 'message': '模板更新成功'})
        else:
            return jsonify({'status': 'error', 'message': '模板更新失败'})
    except Exception as e:
        logger.error(f"更新用户模板失败: {e}")
        return jsonify({'status': 'error', 'message': f'模板更新失败: {str(e)}'})


@app.route('/api/templates/user/<name>', methods=['DELETE'])
def delete_user_template(name):
    """API: 删除用户自定义模板"""
    try:
        if tm.delete_user_template(name):
            return jsonify({'status': 'success', 'message': '模板删除成功'})
        else:
            return jsonify({'status': 'error', 'message': '模板删除失败或模板不存在'})
    except Exception as e:
        logger.error(f"删除用户模板失败: {e}")
        return jsonify({'status': 'error', 'message': f'模板删除失败: {str(e)}'})


@app.route('/api/debug/session', methods=['GET'])
def get_session_debug():
    """API: 调试会话数据"""
    try:
        entities = session.get('entities', [])
        selected_templates = session.get('selected_templates', [])
        report_paths = session.get('report_paths', {})

        return jsonify({
            'status': 'success',
            'session_data': {
                'entities': entities,
                'selected_templates_count': len(selected_templates),
                'selected_templates': selected_templates,
                'report_paths': list(report_paths.keys()) if report_paths else []
            }
        })
    except Exception as e:
        logger.error(f"获取会话数据失败: {e}")
        return jsonify({'status': 'error', 'message': f'获取会话数据失败: {str(e)}'})


@app.route('/api/folder/open', methods=['POST'])
def open_folder():
    """API: 打开报告文件夹"""
    try:
        import os
        import platform
        import subprocess

        # 报告文件夹路径
        report_dir = config.reports_dir

        # 根据操作系统打开文件夹
        if platform.system() == 'Windows':
            subprocess.Popen(f'explorer "{report_dir}"')
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', report_dir])
        else:
            subprocess.Popen(['xdg-open', report_dir])

        return jsonify({'status': 'success', 'message': '文件夹已打开'})
    except Exception as e:
        logger.error(f"打开文件夹失败: {e}")
        return jsonify({'status': 'error', 'message': f'打开文件夹失败: {str(e)}'})


@app.route('/api/folder/open-screenshots', methods=['POST'])
def open_screenshots_folder():
    """API: 打开人工核查截图文件夹"""
    try:
        import os
        import platform
        import subprocess

        # 人工核查截图文件夹路径
        screenshots_dir = config.screenshots_dir

        # 根据操作系统打开文件夹
        if platform.system() == 'Windows':
            subprocess.Popen(f'explorer "{screenshots_dir}"')
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', screenshots_dir])
        else:
            subprocess.Popen(['xdg-open', screenshots_dir])

        return jsonify({'status': 'success', 'message': '截图文件夹已打开'})
    except Exception as e:
        logger.error(f"打开截图文件夹失败: {e}")
        return jsonify({'status': 'error', 'message': f'打开截图文件夹失败: {str(e)}'})


@app.route('/api/manual-verify/urls', methods=['GET'])
def get_manual_verify_urls():
    """API: 获取所有需要人工核查的URL列表"""
    try:
        # 获取会话中保存的主体和选择的模板
        entities = session.get('entities', [])
        selected_template_names = session.get('selected_templates', [])

        if not entities:
            return jsonify({'status': 'error', 'message': '请先输入需要核查的主体'})

        # 获取模板详细信息
        templates = tm.load_templates()
        selected_templates = {}
        for template_name in selected_template_names:
            if template_name in templates:
                selected_templates[template_name] = templates[template_name]

        # 筛选出人工核查模板
        manual_templates = {name: template for name, template in selected_templates.items() if template.category == 'manual'}

        if not manual_templates:
            return jsonify({'status': 'error', 'message': '没有选择需要人工核查的网页'})

        # 生成所有主体和人工核查模板对应的URL
        from everify.core.services.url_generator import URLGenerator
        manual_urls = URLGenerator.generate_manual_verify_urls(entities, manual_templates)

        return jsonify({'status': 'success', 'urls': manual_urls})
    except Exception as e:
        logger.error(f"获取人工核查URL失败: {e}")
        return jsonify({'status': 'error', 'message': f'获取人工核查URL失败: {str(e)}'})


@app.route('/api/verify/start', methods=['POST'])
def start_verification():
    """API: 开始执行核查操作"""
    try:
        # 确保logger已初始化
        from everify.core.utils.logger import setup_logging, logger
        setup_logging()

        # 获取会话中保存的主体和选择的模板
        entities = session.get('entities', [])
        selected_template_names = session.get('selected_templates', [])

        if not entities:
            return jsonify({'status': 'error', 'message': '请先输入需要核查的主体'})

        if not selected_template_names:
            return jsonify({'status': 'error', 'message': '请先选择需要核查的网页源'})

        # 获取模板详细信息
        templates = tm.load_templates()
        selected_templates = {}
        for template_name in selected_template_names:
            if template_name in templates:
                selected_templates[template_name] = templates[template_name]

        if not selected_templates:
            return jsonify({'status': 'error', 'message': '未能找到选择的模板'})

        # 创建操作工厂和自动核查操作
        from everify.core.operations.operation_factory import OperationFactory
        from everify.core.services.url_generator import URLGenerator
        from everify.core.services.report_generator import ReportGenerator
        from everify.core.services.verify_service import VerifyService

        url_generator = URLGenerator()
        report_generator = ReportGenerator(config)

        operation_factory = OperationFactory()
        auto_verify_operation = operation_factory.create_auto_verify_operation(
            url_generator, VerifyService(config), report_generator
        )

        # 执行核查操作
        result = auto_verify_operation.execute(entities, selected_templates)

        if result.success:
            # 保存报告路径到会话
            session['report_paths'] = result.data['report_paths']
            return jsonify({
                'status': 'success',
                'message': result.data['message'],
                'report_count': len(result.data['report_paths'])
            })
        else:
            return jsonify({'status': 'error', 'message': result.error})
    except Exception as e:
        import logging
        import traceback
        logging.error(f"执行核查失败: {e}")
        logging.error(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': f'执行核查失败: {str(e)}', 'stack': traceback.format_exc()})


@app.route('/api/bribery-verify/start', methods=['POST'])
def start_bribery_verification():
    """API: 开始执行涉贿核查操作（搜索引擎查询）"""
    try:
        # 确保logger已初始化
        from everify.core.utils.logger import setup_logging, logger
        setup_logging()

        # 获取会话中保存的主体
        entities = session.get('entities', [])

        if not entities:
            return jsonify({'status': 'error', 'message': '请先输入需要核查的主体'})

        # 创建操作工厂和搜索引擎查询操作
        from everify.core.operations.operation_factory import OperationFactory

        operation_factory = OperationFactory()
        search_operation = operation_factory.create_search_engine_query_operation(config)

        # 执行搜索引擎查询操作
        result = search_operation.execute(entities)

        if result.success:
            # 保存报告路径到会话
            session['report_paths'] = result.data['report_paths']
            return jsonify({
                'status': 'success',
                'message': result.data['message'],
                'report_count': len(result.data['report_paths'])
            })
        else:
            return jsonify({'status': 'error', 'message': result.error})
    except Exception as e:
        import logging
        import traceback
        logging.error(f"执行涉贿核查失败: {e}")
        logging.error(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': f'执行涉贿核查失败: {str(e)}', 'stack': traceback.format_exc()})


@app.route('/api/manual-verify/start', methods=['POST'])
def start_manual_verification():
    """API: 开始人工核查"""
    try:
        # 确保logger已初始化
        from everify.core.utils.logger import setup_logging, logger
        setup_logging()

        # 获取会话中保存的主体和选择的模板
        entities = session.get('entities', [])
        selected_template_names = session.get('selected_templates', [])
        report_paths = session.get('report_paths', {})

        if not entities:
            return jsonify({'status': 'error', 'message': '请先输入需要核查的主体'})

        if not report_paths:
            return jsonify({'status': 'error', 'message': '请先执行自动核查，生成报告后再进行人工核查'})

        # 创建操作工厂和人工截图插入操作
        from everify.core.operations.operation_factory import OperationFactory
        from everify.core.services.report_generator import ReportGenerator

        report_generator = ReportGenerator(config)

        operation_factory = OperationFactory()
        manual_screenshot_operation = operation_factory.create_manual_screenshot_operation(
            report_generator, config
        )

        # 执行人工截图插入操作
        result = manual_screenshot_operation.execute(
            entities, report_paths, config.screenshots_dir
        )

        if result.success:
            return jsonify({
                'status': 'success',
                'message': result.data['message']
            })
        else:
            return jsonify({'status': 'error', 'message': result.error})
    except Exception as e:
        import logging
        import traceback
        logging.error(f"执行人工核查失败: {e}")
        logging.error(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': f'执行人工核查失败: {str(e)}', 'stack': traceback.format_exc()})


def main():
    """Web 应用入口函数"""
    import webbrowser
    import time
    import signal
    import sys

    def signal_handler(sig, frame):
        print('\n收到终止信号，正在关闭应用程序...')
        sys.exit(0)

    # 设置信号处理程序
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print('启动 Everify 网页核查自动化系统...')
    print('访问地址: http://localhost:5000')

    # 只在首次启动时自动打开网页，避免调试模式下多次打开
    import os
    if 'WERKZEUG_RUN_MAIN' not in os.environ:
        webbrowser.open('http://localhost:5000')

    # 启动 Flask 应用 - 禁用自动重载以避免监视虚拟环境
    try:
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print('\n应用程序已关闭')


if __name__ == '__main__':
    main()
