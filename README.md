# Description

KT가 제공하는 ucloud watch 는 무료이지만 최대 7일 까지만 볼 수 있다. 

또한 GUI는 아마존의 cloud watch에 비하면, 그대로 사용하기 부족하다.

이 프로젝트는 아래의 두가지를 제공 한다 :

1. 7일 이상의 ucloud watch 데이터 저장

2. 보기 쉬운 GUI 제공

# Structure

structure image here

Grafana image here

# Usages

## 데이터 수집기(main.py) 설정법

./../conf/conf.yml 의 내용을 수정하면 된다.

## 데이터 수집기(main.py) 사용법

main.py 는 수집한 ucloud watch 데이터를 지정한 influxdb에 입력하는 역할을 한다.

KT는 5분 단위로 최소/최대/평균 값을 리턴 하므로, 아래와 같이 crontab 에 등록하면 '지금'~'5분 전' 사이에 입력된 ucloud watch 데이터를 가져온다 :

```
*/5 * * * * python main.py "`date +\%Y-\%m-\%dT\%H:\%M:00.000 -d '-5 mins'`" "`date +\%Y-\%m-\%dT\%H:\%M:00.000`"
```

특정 시점의 데이터를 ucloud watch 로 부터 가져오고 싶다면, 수동으로 실행하되 첫번째 인자를 '조회 시작 시간', 두번째 인자를 '조회 완료 시간' 으로 지정하면 된다.

단, ucloud watch는 7일치 이상의 데이터는 가지고 있지 않다는 점을 잊지 말자.

## Grafana 설정법

데이터 수집기가 수집한 정보는 influxdb에 '계정별로' 기록 된다. 아래의 이미지와 같이 influxdb의 데이터베이스 명을, conf.yml에 적은것과 같이 바꿔준다.

계정이 다수인 경우, datasource를 다수로 만들면 되겠다.

## Grafana 사용법

기본설정은 grafana_data/grafana.db 에 있다(SQLite). 해당 디렉토리를 Grafana의 /var/lib/grafana로 마운트 하면 된다.

cpu/memory/network/disk io 등의 기본 대쉬보드가 있으니 그대로 쓰면 되겠다.

더 추가하거나 숮어하고 싶다면, grafana.org에서 사용법을 익힌 뒤 하면 되겠다.

# Dependencies

아래의 Python 2.7 패키지에 의존성이 있다 :

```
influxdb
```

아래의 Docker image에 의존성이 있다 :

```
influxdb:1.2
grafana/grafana:4.1.2
```

# Installation

1. python influxdb package install 

```
pip install influxdb
```

2. docker install

manual link here

3. containers 

```
docker run -d -p 3000:3000 -e "GF_SECURITY_ADMIN_PASSWORD=secret" -v VOLUME_TO_MOUNT:/var/lib/grafana:rw --name grafana4.1.2 grafana/grafana:4.1.2

docker run -d -p 8083:8083 -p 8086:8086 -v VOLUME_TO_MOUNT:/var/lib/influxdb:rw --name inluxdb1.2 influxdb:1.2
```

# Note

