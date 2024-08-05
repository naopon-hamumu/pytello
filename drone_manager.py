import logging # ログの追跡
import socket # アプリケーション間の通信の出入り口
import sys # Pythonのインタプリタや実行環境に関連した変数や関数がまとめられている
import threading # 並列処理をさせる
import time

# logging.INFO：情報ログ
# sys.stdout：print関数よりもよりシステマチックな標準出力
# sys自体がprint関数よりもさまざまなことができる
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

class DroneManager(object):
  def __init__(self, host_ip='192.168.10.2', host_port=8889,
               drone_ip='192.168.10.1', drone_port=8889):
    self.host_ip = host_ip
    self.host_port = host_port
    self.drone_ip = drone_ip
    self.drone_port = drone_port
    self.drone_address = (drone_ip, drone_port)
    # ソケットの作成
    # アドレスファミリー => AF_INET：IPv4インターネットプロトコル
    # ソケットタイプ => SOCK_DGRAM：UDPソケット通信で利用される
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # ローカルのアドレスにバインド
    self.socket.bind((self.host_ip, self.host_port))

    self.response = None
    self.stop_event = threading.Event()
    # タプル型：要素の順番を変えず、データ型が固定の場合に使用される
    response_thread = threading.Thread(target=self.receive_response,
                                       args=(self.stop_event, ))
    self._response_thread.start()

    self.send_command('command')
    self.send_command('streamon')

  def receive_response(self, stop_event):
    while not stop_event.is_set():
      try:
        self.response, ip = self.socket.recvfrom(3000)
        logger.info({'action': 'receive_response',
                    'response': self.response})
      except socket.error as ex:
        logger.error({'action': 'receive_response',
                     'ex': ex})
        break

  def __dell__(self):
    self.stop()

  def stop(self):
    self.stop_event.set()
    # ソケットのクローズ&ファイルディスクリプタの削除
    self.socket.close()

  def send_command(self, command):
    logger.info({'action': 'send_command', 'command': command})
    self.socket.sendto(command.encode('utf-8'), self.drone_address)

  def takeoff(self):
    self.send_command('takeoff')

  def land(self):
    self.send_command('land')

if __name__ == '__main__':
  drone_manager = DroneManager()
  drone_manager.takeoff()

  time.sleep(10)

  drone_manager.land()
  drone_manager.stop()
