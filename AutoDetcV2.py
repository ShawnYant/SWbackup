import paramiko
import time
import os
import pandas as pd
from datetime import datetime

def detect_device_type(shell):
    shell.send('\n')
    time.sleep(2)
    if shell.recv_ready():
        output = shell.recv(65535).decode('utf-8')
        print(f'Device prompt detection output: {output}')  # 调试输出
        if '>' in output:  # 检测到用户视图提示符
            # 尝试进入系统视图
            shell.send('system-view\n')
            time.sleep(2)
            if shell.recv_ready():
                output = shell.recv(65535).decode('utf-8')
                print(f'System view detection output: {output}')  # 调试输出
                if ']' in output:
                    return 'huawei'
        elif '#' in output:  # 特权模式提示符
            # 尝试识别戴尔设备
            shell.send('show version\n')
            time.sleep(2)
            if shell.recv_ready():
                output = shell.recv(65535).decode('utf-8')
                print(f'Show version output: {output}')  # 调试输出
                if 'Dell' in output or 'dell' in output:
                    return 'dell'
            return 'cisco'
    return 'unknown'

def backup_switch_config(switch_ip, port, username, password, output_path):
    try:
        # 创建SSH客户端对象
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 建立SSH连接
        print(f'Connecting to {switch_ip} on port {port}...')
        ssh.connect(switch_ip, port=port, username=username, password=password, timeout=30)

        # 创建一个交互式Shell会话
        shell = ssh.invoke_shell()
        time.sleep(2)  # 等待Shell会话建立

        # 检测设备类型
        device_type = detect_device_type(shell)
        if device_type == 'unknown':
            raise ValueError(f"无法确定设备类型: {switch_ip}")

        print(f'Device {switch_ip} detected as {device_type}.')

        if device_type == 'huawei':
            # 获取当前配置
            shell.send('display current-configuration\n')
        elif device_type == 'cisco':
            # 进入特权模式
            shell.send('enable\n')
            time.sleep(1)
            # 输入密码（假设密码与登录密码相同）
            shell.send(password + '\n')
            time.sleep(1)
            # 获取当前配置
            shell.send('show running-config\n')
        elif device_type == 'dell':
            # 获取当前配置
            shell.send('show running-config\n')
        else:
            raise ValueError(f"不支持的设备类型: {device_type}")

        time.sleep(1)

        # 循环读取输出直到完整配置显示完成
        output = ""
        more_prompt_huawei = "--- More ---"
        more_prompt_cisco = "--More--"
        more_prompt_dell = "--more--"
        end_prompt_huawei = "]"
        end_prompt_cisco = "#"
        end_prompt_dell = "#"

        while True:
            if shell.recv_ready():
                data = shell.recv(65535).decode('utf-8')
                output += data
                print(f'Received data: {data}')  # 调试输出
                if (more_prompt_huawei in data and device_type == 'huawei') or \
                   (more_prompt_cisco in data and device_type == 'cisco') or \
                   (more_prompt_dell in data and device_type == 'dell'):  # 检测到分页提示符
                    shell.send(' ')  # 发送空格以继续显示下一页
                    time.sleep(0.5)  # 等待设备响应
                elif (end_prompt_huawei in data and device_type == 'huawei') or \
                     (end_prompt_cisco in data and device_type == 'cisco') or \
                     (end_prompt_dell in data and device_type == 'dell'):  # 假设提示符包含 ']' 或 '#'
                    break
            time.sleep(0.5)  # 减少等待时间以加快读取速度

        # 关闭Shell和SSH连接
        shell.close()
        ssh.close()

        # 保存备份文件
        filename = os.path.join(output_path, f'{switch_ip}.cfg')
        with open(filename, 'w') as config_file:
            config_file.write(output)

        print(f'设备 {switch_ip} ({device_type}) 的配置文件备份完成，保存为 {filename}。')

        return True, None  # 表示成功

    except Exception as e:
        return False, str(e)  # 返回错误信息

    finally:
        try:
            if ssh.get_transport().is_active():
                ssh.close()
        except:
            pass

def main():
    # 配置桌面路径
    desktop_path = 'D:'

    # 读取Excel文件中的交换机信息
    excel_path = 'D:.xlsx'
    df = pd.read_excel(excel_path)

    # 获取当前日期
    current_date = datetime.now().strftime('%Y-%m-%d')

    # 创建保存文件夹
    excel_filename = os.path.splitext(os.path.basename(excel_path))[0]
    output_folder_name = f"{excel_filename}_{current_date}"
    output_path = os.path.join(desktop_path, output_folder_name)
    os.makedirs(output_path, exist_ok=True)

    # 记录失败的IP和错误信息
    failed_switches = []

    # 遍历交换机列表，备份配置文件
    for _, row in df.iterrows():  # 使用 _ 忽略 index
        switch_ip = row['IP']
        port = int(row['Port'])  # 从Excel中读取端口号
        username = row['Username']
        password = row['Password']
        success, error = backup_switch_config(switch_ip, port, username, password, output_path)
        if not success:
            failed_switches.append((switch_ip, error))
            print(f'备份设备 {switch_ip} 的配置文件失败: {error}')

    # 保存失败的IP和错误信息到txt文件
    if failed_switches:
        failed_log_path = os.path.join(output_path, 'backup_failures.txt')
        with open(failed_log_path, 'w') as log_file:
            for switch_ip, error in failed_switches:
                log_file.write(f'设备 {switch_ip} 备份失败，原因: {error}\n')

        print(f'备份失败的设备列表已保存到 {failed_log_path}。')

if __name__ == "__main__":
    main()
