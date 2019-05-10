[![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/big-data-europe/docker-hadoop-spark-workbench)

# How to use HDFS/Spark Workbench

To start an HDFS/Spark Workbench by one single command:
```
    docker-compose up -d
```

By default, we set 1 master, 6 workers inside the configuration. Nevertheless, ```docker-compose``` works to scale up the cluster capacity, users can just modify ```docker-compose.yml``` by concatenating the following configuration:

```
 spark-workerN:
    image: jingweizuo/pyspark-worker
    container_name: spark-workerN
    depends_on:
      - spark-master
    environment:
      - SPARK_MASTER=spark://spark-master:7077
    ports:
      - 808N:8081
    env_file:
      - ./hadoop.env
```  

``` jingweizuo/pyspark-master``` and ``` jingweizuo/pyspark-worker``` contain Python3 enviroment support for Apache Spark, as well as several common packages:

* pyspark 
* numpy 
* pandas 
* astropy 
* Cython 
* sklearn 
* tsfresh 
* line_profiler

* Users can feel free to import the libraries by updating the Docker image

## Starting workbench with Hive support

Before starting the next command, check that the previous service is running correctly (with docker logs servicename).  

```
docker-compose -f docker-compose-hive.yml up -d namenode hive-metastore-postgresql
docker-compose -f docker-compose-hive.yml up -d datanode hive-metastore
docker-compose -f docker-compose-hive.yml up -d hive-server
docker-compose -f docker-compose-hive.yml up -d spark-master spark-worker spark-notebook hue
```

## Interfaces

* Namenode: http://localhost:50070
* Datanode: http://localhost:50075
* Spark-master: http://localhost:8080
* Spark-notebook: http://localhost:9001
* Hue (HDFS Filebrowser): http://localhost:8088/home

## Important

When opening Hue, you might encounter ```NoReverseMatch: u'about' is not a registered namespace``` error after login. I disabled 'about' page (which is default one), because it caused docker container to hang. To access Hue when you have such an error, you need to append /home to your URI: ```http://docker-host-ip:8088/home```

## Docs
* [Motivation behind the repo and an example usage @BDE2020 Blog](http://www.big-data-europe.eu/scalable-sparkhdfs-workbench-using-docker/)

## Count Example for Spark Notebooks
```
val spark = SparkSession
  .builder()
  .appName("Simple Count Example")
  .getOrCreate()

val tf = spark.read.textFile("/data.csv")
tf.count()
```

## Maintainer
* jingwei dot zuo at uvsq dot fr

