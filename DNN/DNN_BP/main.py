from io import BytesIO
from pathlib import Path
import cairo
import subprocess
from nicegui import ui, app
import json
from nicegui.events import MouseEventArguments
import math

card_css = '''
position: relative;
width: 200px;
height: 100px;
margin: 30px;
box-shadow: 20px 20px 50px rgba(0, 0, 0, 0.5);
border-radius: 15px;
background: rgba(255, 255, 255, 0.1);
overflow: hidden;
display: flex;
justify-content: center;
align-items: center;
border-top: 1px solid rgba(255, 255, 255, 0.5);
border-left: 1px solid rgba(255, 255, 255, 0.5);
backdrop-filter: blur(5px);
'''
text_css = '''
backdrop-filter: blur(5px);
position: relative;
display: inline-block;
padding: 8px 20px;
margin-top: 15px;
background: #fff;
color: #000;
border-radius: 15px;
text-decoration: none;
font-weight: 500;
box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
'''
with open("DNN/config/config.json", "r", encoding="utf-8") as f:
        sample_config = json.load(f)
class Png():
    def __init__(self, path):
        self.PNG_PATH = Path(path)
        self.output = BytesIO()
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 800)
        self.context = cairo.Context(self.surface)
        self.context.set_source_rgb(0, 0, 0)
        self.context.rectangle(0, 0, 800, 800)
        self.context.fill()
    def generate_png(self) -> bytes:
        self.surface.write_to_png(self.output)
        self.surface.finish()
        return self.output.getvalue()
    def draw(self, x, y):
        self.context.set_source_rgb(255, 255, 255)
        self.context.arc(x, y, 25, 0, 2*math.pi)
        self.context.fill()
    def clear(self):
        self.output = BytesIO()
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 800)
        self.context = cairo.Context(self.surface)
        self.context.set_source_rgb(0, 0, 0)
        self.context.rectangle(0, 0, 800, 800)
        self.context.fill()
    def finish(self):
        self.PNG_PATH.write_bytes(self.generate_png())

@ui.page('/handwrite')
def handwrite():
    png = Png(sample_config['test_image_file'])
    l = ui.label('up')
    l.visible = False
    ui.link('返回', '/').style(text_css)
    def on_mouse(e: MouseEventArguments):
        if e.type == 'mouseup':
            l.text = 'up'
        elif e.type == 'mousedown':
            l.text = 'down'
        elif e.type == 'mousemove' and l.text == 'down':
            content.content += f'<circle cx="{e.image_x}" cy="{e.image_y}" r="25" fill="Black" stroke="Black" stroke-width="4" />'
            png.draw(e.image_x, e.image_y)
    content = ui.interactive_image(
    size=(800, 800), cross=True,
    on_mouse=on_mouse, events=['mousemove', 'mousedown', 'mouseup']).classes('w-64 bg-blue-50').style('margin: 0 auto;')
    def run():
        timer.activate()
        result.visible = True
        with open('DNN/DNN_BP/ways.json', 'r', encoding="utf-8") as w:
            config = json.load(w)
        with open('DNN/DNN_BP/ways.json', 'w', encoding="utf-8") as w:
            config["ways"] = "run"
            json.dump(config, w, ensure_ascii=False)
        with open('DNN/DNN_BP/logs.txt', 'w', encoding="utf-8") as t:
            t.write('')
        script_to_run = 'DNN/DNN_BP/run.py'
        python_interpreter = sample_config['python_interpreter']
        subprocess.Popen([python_interpreter, script_to_run])
    

    def update_result():
        with open('DNN/DNN_BP/logs.txt', 'r', encoding="utf-8") as t:
            text = t.read()
            if text != '':
                result.push('FINISHED')
                result.push(text)
                timer.deactivate()
            else :
                result.push('RUNING...')
                 
    timer = ui.timer(2, update_result, active=False)
    with ui.row().style('align-items: center; margin: 0 auto;'):
        ui.button('清除', on_click=lambda: (content.set_content(''), png.clear(), ui.notify('已清除')))
        ui.button('确定', on_click=lambda: (png.finish(), ui.notify('已保存至output.png')))
        ui.button('识别', on_click=run)
    result = ui.log(max_lines=25).style('height: 150px;width: 800px; margin: 0 auto;')
    result.visible = False   
@ui.page('/learnfrom')
def learnfrom():
    ui.link('返回', '/').style(text_css)
    with ui.dialog() as dialog, ui.card():
        ui.label('APP界面点击链接后无法返回，解决方法为：重新启动APP')
        ui.button('Close', on_click=dialog.close)
    # dialog.open()
    with ui.column().style('align-items: center; margin: 0 auto;'):
        with ui.card().style(card_css):
            ui.link('人工智能---BP神经网络（数字识别）', r'https://blog.csdn.net/qq_36347365/article/details/87010365#:~:text=%E6%9E%84%E9%80%A0%20BP%20%E7%A5%9E%E7%BB%8F%E7%BD%91%E7%BB%9C%E5%B9%B6%E7%94%A8%E6%89%8B%E5%86%99%E6%95%B0%E5%AD%97%E7%9A%84%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E8%AE%AD%E7%BB%83%EF%BC%8C%E4%BD%BF%E5%85%B6%E5%85%B7%E6%9C%89%E8%AF%86%E5%88%AB%E6%89%8B%E5%86%99%E6%95%B0%E5%AD%97%E7%9A%84%E8%83%BD%E5%8A%9B%E3%80%82%20%E6%96%B9%E6%B3%95%E6%8F%8F%E8%BF%B0%EF%BC%9A,BP%20%EF%BC%88Error%20Back%20Proragation%EF%BC%8C%E8%AF%AF%E5%B7%AE%E5%8F%8D%E4%BC%A0%EF%BC%89%E7%AE%97%E6%B3%95%E6%98%AF%E4%B8%80%E7%A7%8D%E5%8C%85%E5%90%AB%E9%9A%90%E5%B1%82%E7%9A%84%E5%A4%9A%E5%B1%82%E5%89%8D%E9%A6%88%E7%BD%91%E7%BB%9C%E3%80%82%20%E5%AE%83%E7%9A%84%E5%AD%A6%E4%B9%A0%E8%A7%84%E5%88%99%E6%98%AF%E4%BD%BF%E7%94%A8%E8%AF%AF%E5%B7%AE%E7%9A%84%E6%A2%AF%E5%BA%A6%E4%B8%8B%E9%99%8D%E6%B3%95%EF%BC%8C%E9%80%9A%E8%BF%87%E8%AF%AF%E5%B7%AE%E5%8F%8D%E5%90%91%E4%BC%A0%E6%92%AD%E6%9D%A5%E4%B8%8D%E6%96%AD%E8%B0%83%E6%95%B4%E7%BD%91%E7%BB%9C%E7%9A%84%E6%9D%83%E5%80%BC%E5%92%8C%E9%98%88%E5%80%BC%EF%BC%8C%E4%BD%BF%E7%BD%91%E7%BB%9C%E7%9A%84%E8%AF%AF%E5%B7%AE%E6%9C%80%E5%B0%8F%E3%80%82').style(text_css)
        ui.separator()
        with ui.card().style(card_css):
            ui.link('卷积神经网络(CNN)反向传播算法', r'https://www.cnblogs.com/pinard/p/6494810.html').style(text_css)
@ui.page('/readme')
def readme():
    ui.link('返回', '/').style(text_css)
    with ui.tabs().classes('w-full') as tabs:
        one = ui.tab('实验报告')
        two = ui.tab('README')
    with ui.tab_panels(tabs, value=one).classes('w-full'):
        with ui.tab_panel(one):
            with open('实验报告.md', 'r', encoding="utf-8") as t:
                text = t.read()
            ui.markdown(text)
        with ui.tab_panel(two):
            with ui.dialog() as dialog, ui.card():
                ui.label('README部分未开发')
                ui.button('Close', on_click=dialog.close)
            dialog.open()
    
@ui.page('/model')
def model():
    with open('DNN/DNN_BP/logs.txt', 'w', encoding="utf-8") as t:
            t.write('')
    ui.link('返回', '/').style(text_css)
    
    result = ui.log(max_lines=25).style('height: 300px;width: 800px; margin: 0 auto;')

    def update_result():
        with open('DNN/DNN_BP/logs.txt', 'r', encoding="utf-8") as t:
            text = t.read()
            if text != '':
                result.push('FINISHED')
                result.push(text)
                timer.deactivate()
            else :
                result.push('RUNING...')
                 
    timer = ui.timer(2.0, update_result, active=False)

    def on_click():
        with open('DNN/DNN_BP/ways.json', 'r', encoding="utf-8") as w:
            config = json.load(w)
        with open('DNN/DNN_BP/ways.json', 'w', encoding="utf-8") as w:
            if switch.value:
                config["ways"] = "train"
            else:
                config["ways"] = "test"
            json.dump(config, w, ensure_ascii=False)
        with open('DNN/DNN_BP/logs.txt', 'w', encoding="utf-8") as t:
            t.write('')
        timer.activate()
        script_to_run = 'c:/Users/MILI/Desktop/python_project/手写数字识别/DNN/DNN_BP/run.py'
        python_interpreter = r'C:/Users/MILI/miniconda3/envs/python_3.10/python.exe'
        subprocess.Popen([python_interpreter, script_to_run])

    switch = ui.switch('是否训练模型', value=False, on_change=lambda: ui.notify('请务必确保参数配置完毕后运行')).style('margin: 0 auto;')
    ui.button('run', on_click=on_click).style('margin: 0 auto;')
    s = ui.spinner(size='lg').bind_visibility_from(timer, 'active')

@ui.page('/')    
def main():
    # 读取配置文件
    with open("DNN\config\config.json", "r", encoding="utf-8") as f:
        sample_config = json.load(f)
    app.add_static_files('/static', 'static')
    with ui.tabs().classes('w-full') as tabs:
        one = ui.tab('首页')
        two = ui.tab('参数配置')
    with ui.tab_panels(tabs, value=one).classes('w-full'):
        with ui.tab_panel(one):
            with ui.column().style('align-items: center; margin: 0 auto;'):
                with ui.card().style(card_css):
                    ui.link('训练or测试模型', '/model').style(text_css)
                ui.separator()
                with ui.card().style(card_css):
                    ui.link('手写识别', '/handwrite').style(text_css)
                ui.separator()
                with ui.card().style(card_css):
                    ui.link('实验报告orREADME', '/readme').style(text_css)
                ui.separator()
                with ui.card().style(card_css):
                    ui.link('学习参考内容', '/learnfrom').style(text_css)
                ui.separator()
        with ui.tab_panel(two):
            copy_config = sample_config.copy()
            for key in sample_config:
                text = str(sample_config[key])
                with ui.row():
                    ui.input(label=key, value=text).style('width:550px;').bind_value_to(copy_config, key)
            def save():
                sample_config = copy_config.copy()
                with open("DNN\config\config.json", "w", encoding="utf-8") as f:
                    json.dump(sample_config, f, ensure_ascii=False)
                ui.notify('保存成功')

            ui.button('保存', on_click=save)

ui.run(favicon='🚀', native=False, title="Handwritten digit recognition powered by Nicegui")

