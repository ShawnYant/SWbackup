import paramiko
import time
import os
import pandas as pd
from datetime import datetime

def backup_switch_config(switch_ip, username, password, port, output_path):
    try:
        # 创建SSH客户端对象
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 建立SSH连接
        ssh.connect(switch_ip, port=port, username=username, password=password, timeout=30)

        # 创建一个交互式Shell会话
        shell = ssh.invoke_shell()
        time.sleep(1)  # 等待Shell会话建立

        # 进入系统视图
        shell.send('system-view\n')
        time.sleep(1)

        # 获取当前配置
        shell.send('display current-configuration\n')
        time.sleep(1)

        # 循环读取输出直到完整配置显示完成
        output = ""
        more_prompt = "More"
        end_prompt = "]"
        while True:
            if shell.recv_ready():
                data = shell.recv(65535).decode('utf-8')
                output += data
                if more_prompt in data:  # 检测到分页提示符
                    shell.send(' ')  # 发送空格以继续显示下一页
                elif end_prompt in data:  # 假设提示符包含 ']'
                    break
            time.sleep(0.5)  # 减少等待时间以加快读取速度

        # 关闭Shell和SSH连接
        shell.close()
        ssh.close()

        # 保存备份文件
        filename = os.path.join(output_path, f'{switch_ip}.cfg')
        with open(filename, 'w') as config_file:
            config_file.write(output)

        print(f'交换机 {switch_ip} 的配置文件备份完成，保存为 {filename}。')

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
    # 配置保存路径
    desktop_path = 'D:/来个路径'

    # 读取Excel文件中的交换机信息
    excel_path = 'D:/您表儿在哪儿就写哪儿'
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
    for index, row in df.iterrows():
        switch_ip = row['IP']
        username = row['Username']
        password = row['Password']
        port = int(row['Port'])  # 从Excel中读取端口号
        success, error = backup_switch_config(switch_ip, username, password, port, output_path)
        if not success:
            failed_switches.append((switch_ip, error))
            print(f'备份交换机 {switch_ip} 的配置文件失败: {error}')

    # 保存失败的IP和错误信息到txt文件
    if failed_switches:
        failed_log_path = os.path.join(output_path, 'backup_failures.txt')
        with open(failed_log_path, 'w') as log_file:
            for switch_ip, error in failed_switches:
                log_file.write(f'交换机 {switch_ip} 备份失败，原因: {error}\n')

        print(f'备份失败的交换机列表已保存到 {failed_log_path}。')

if __name__ == "__main__":
    main()
