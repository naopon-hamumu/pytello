import logging # ログの追跡
import contextlib # try文の省略をさせる
import socket # アプリケーション間の通信の出入り口
import sys # Pythonのインタプリタや実行環境に関連した変数や関数がまとめられている
import threading # 並列処理をさせる
import time

# logging.INFO：情報ログ
# sys.stdout：print関数よりもよりシステマチックな標準出力
# sys自体がprint関数よりもさまざまなことができる
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

DEFAULT_DISTANCE = 0.30
DEFAULT_SPEED = 10
DEFAULT_DEGREE = 10

class DroneManager(object):
    def __init__(self, host_ip='192.168.10.2', host_port=8889,
                drone_ip='192.168.10.1', drone_port=8889,
                is_imperial=False, speed=DEFAULT_SPEED):
        self.host_ip = host_ip
        self.host_port = host_port
        self.drone_ip = drone_ip
        self.drone_port = drone_port
        self.drone_address = (drone_ip, drone_port)
        self.is_imperial = is_imperial
        self.speed = speed
        # ソケットの作成
        # アドレスファミリー => AF_INET：IPv4インターネットプロトコル
        # ソケットタイプ => SOCK_DGRAM：UDPソケット通信で利用される
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # ローカルのアドレスにバインド
        self.socket.bind((self.host_ip, self.host_port))

        self.response = None
        self.stop_event = threading.Event()
        # タプル型：要素の順番を変えず、データ型が固定の場合に使用される
        self._response_thread = threading.Thread(target=self.receive_response,
                                        args=(self.stop_event, ))
        self._response_thread.start()

        self.patrol_event = None
        self.is_patrol = False
        self._patrol_semaphore = threading.Semaphore(1)
        self._thread_patrol = None

        self.send_command('command')
        self.send_command('streamon')
        self.set_speed(self.speed)

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

        if self.response is None:
            response = None
        else:
            response = self.response.decode('utf-8')
        self.response = None
        return response

    def takeoff(self):
        self.send_command('takeoff')

    def land(self):
        self.send_command('land')

    def move(self, direction, distance):
        distance = float(distance)
        if self.is_imperial:
            distance = int(round(distance * 30.48)) # 単位フィートへ変換
        else:
            distance = int(round(distance * 100))
        return self.send_command(f'{direction} {distance}')

    def up(self, distance=DEFAULT_DISTANCE):
        return self.move('up', distance)

    def down(self, distance=DEFAULT_DISTANCE):
        return self.move('down', distance)

    def left(self, distance=DEFAULT_DISTANCE):
        return self.move('left', distance)

    def right(self, distance=DEFAULT_DISTANCE):
        return self.move('right', distance)

    def forward(self, distance=DEFAULT_DISTANCE):
        return self.move('forward', distance)

    def back(self, distance=DEFAULT_DISTANCE):
        return self.move('back', distance)

    def set_speed(self, speed):
        return self.send_command(f'speed {speed}')

    def clockwise(self, degree=DEFAULT_DEGREE):
        return self.send_command(f'cw {degree}')

    def counter_clockwise(self, degree=DEFAULT_DEGREE):
        return self.send_command(f'ccw {degree}')

    def flip_front(self):
        return self.send_command('flip f')

    def flip_back(self):
        return self.send_command('flip b')

    def flip_left(self):
        return self.send_command('flip l')

    def flip_right(self):
        return self.send_command('flip r')

    def patrol(self):
        if not self.is_patrol:
            self.patrol_event = threading.Event()
            self._thread_patrol = threading.Thread(
                target=self._patrol,
                args=(self._patrol_semaphore, self.patrol_event,))
            self._thread_patrol.start()
            self.is_patrol = True

    def stop_patrol(self):
        if self.is_patrol:
            self.patrol_event.set()
            retry = 0
            while self._thread_patrol.is_alive():
                time.sleep(0.3)
                if retry > 300:
                    break
                retry += 1
                self.is_patrol = False

    def _patrol(self, semaphore, stop_event):
        is_acquire = semaphore.acquire(blocking=False)
        if is_acquire:
            logger.info({'action': '_patrol', 'status': 'acquire'})
            with contextlib.ExitStack() as stack:
                stack.callback(semaphore.release)
                status = 0
                while not stop_event.is_set():
                    status += 1
                    if status == 1:
                        self.up()
                    if status == 2:
                        self.clockwise(90)
                    if status == 3:
                        self.down()
                    if status == 4:
                        status = 0
                    time.sleep(5)
        else:
            logger.warning({'action': '_patrol', 'status': 'not_acquire'})

if __name__ == '__main__':
    drone_manager = DroneManager()

    drone_manager.set_speed(100)
    drone_manager.takeoff()
    time.sleep(10)

    drone_manager.patrol()
    time.sleep(10)
    drone_manager.stop_patrol()
    time.sleep(5)

    drone_manager.land()
    drone_manager.stop()
