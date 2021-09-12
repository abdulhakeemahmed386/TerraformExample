#!/usr/bin/env python

"""
This program  is used as a service to configure systems

"""
import sys

sys.path.insert=(0, '/usr/lib/python2.7/site-packages')

import os
import sh
import boto3
import requets
import datetime
import time
import json
import yaml
import logging
import logging.config
import systemd_stopper

from dyconf.utyi import S3Utils, SafeScheduler, config_parser, file_handler
from dyconf.configuratorsimport *
from dyconf.customex import *
from dateutil.tz import tzutc
from dateutil.relativedelta import relativedelta

def run():

"""
check new configuration is availiable in s3 bucket

update status success or failure

"""
envar_list=config['envar_list']
env = ''

for e in envar_list:
    if e in config ['properites']. keys():
	env = config['properties'] [e]
	break
    else:
	continue
    if not env:
	logger.error(Cannot find enviroment variable [{}] in infrastructure properties - Exiting '.format (envar_list))
	sys.exit (1)
    if instance_roll == "prum":
	dyconf_bucket = 'envar-dynamic-config-hob-prum-{}'.format(env)
	temp_bucket = 'temp-dynamic-config-hob-prum-{}'.format(env)
    else:
	dyconf_bucket = 'envar-dynamic-config-hob-bsg-{}'.format(env)
	temp_bucket = 'temp-dynamic-config-hob-bsg-{}'.format(env)

    dyconf_bucket_key = '{}-dyconf.yaml'.format(env)
    temp_bucket_key = '{}_{}.json'.format(instance_role, instance_id)
    logger.info('Gettinng last modified datetime')
    skip_upload, lst_modified_ts = __get_last_modified()
    res ={}
    skip_exec = False
    #get dynamic confirguration file if modified
    try:
	skip_exec = __get_dynamic_config_file(bucket_name=dyconf_bucket, bucket_key=dyconf_bucket_key, 
					      lst_modified_dt_;st_modified_ts, env=env)
   #call configurator based on hob role and configurator will return success failure status
   if not skip_exec:
	res =__configure(d_configurator=configurator, dyconf_bucket_key=dyconf_bucket_key,
	temp_bucket_name = temp_bucket)
   except s3ObjectDownloadError as soe:
 	logger.error(
		'New Dynamic Configuration available but failed to download - will updated temporary bucket with failed '
		'status)
	logger.error('Exception --> ' + str(soe))
	res = __generate_failed_response(str(ce))
    except CofiguratorError as ce:
	res = __generate_failed_response(str(ce))

	#Upload status to temporary bucket
	if not skip_exec and not skip_upload:
	   __upload_status(temp_bucket=temp_bucket, temp_bucket_key=temp_bucket_key, data=res)
    else:
	logger.debug('Skipping status upload to temporary S3 bucket {} due to condition'.format(temp_bucket))

    # end of run #

def __upload_status(temp_bucket_name, temp_bucket_key, data):
    """
    Upload status file to temporary S3 bucket
    Removes temporary key file locally one uploaded
    :param temp_bucket_name: Temporary S3 bucket name
    :param temp_bucket_key: Temporary S3 bucket object name i.e. Config Yaml
    :param data: Data to be uploaded to temporary S3 bucket
    :raises:: DyConfUtilsError
    """
    upload_file = os.path.join(path, temp_bucket_key)
    try:
	logger.debug(
		'Creating status file to upload in temporary S3 bucket {} with data)'.format(temp_bucket_namem, data))
	with open(upload_file, mode='w') as key_file:
		json.dump(data, key_file)

	logger.info('Uploading status file {} to temporary S3 bucket {}'.format(temp_buket_key, temp_bucket_name))

	S3_utils.S3_upload_file(temp_bucket_name, temp_bucket_key, path)
    except Exception as e:
	logger.error('Exception occurred while uploading status --> ' + str(e))
	raise DyconfUtilsError('Failed to upload {} to {} '.format(temp_bucket_key, temp_bucket_name))
    else:
	logger.info(##### Complete Dynamic Configuration run Successfully at {} #######'.format (dt.now()))
    finally:
	logger.info('Finally - Deleting temporary key file ' + upload_file)
	os.remove(upload_file)


def __generate_failed_response(error_desc):
    """
    Generates failed response Json object
    Returns json object
    :param error_desc: Error description
    :returns: Response JSON Object
    """
    f_response = {'status: 'Failed', 'description': error_desc}
    return json.dumps(f_response)


def __configure(d_configurator, dyconf_bucket_key, temp_bucket_name):
    """
    Call Configurator to implement configuration
    Get response as json object ('status':'value', 'description': 'value')
    Returns json object 
    :param d_configurator: Dynamic Configurator Instance
    :param dyconf_bucket_key: Dynamic configuration S3 Bucket object name i.e. Config Yaml
    :param temp_bucket_name: Temporary status update S3 bucket
    :returns :: ConfiguratorError
    """


    logger.info('Calling {} ....'.format(this_configurator))
    try:
	response = d_configurator.configure(os.path.join(path, dyconf_bucket_key))
	parsed_res = json.loads(response)
    except DynamicConfiguratorError as e:
	logger.error('{} failed to process dynamic configuration'.format(this_configurator))
	logger.error('Exception --> ' + str(e))
	raise ConfiguratorError(str(e))

    logger.debug('{} responded {}'.format(this_configurator, prased_res['status']))
    status = parsed_res['status'].lower()
    desc = parsed_res['description']

    #write status file and upload to temporary bucket
    logger.info('{c}  returned status  {s} --->'.format(c=this_configurator, s=status))

    if status == 'success':
	logger.info('Will notify success to temporary S3 bucket {}'.format(temp_bucket_name))
    else:
	logger.info('Failure reason - {}\n\tNotify failure to temporary S3 bucket {}'.format(desc, temp_bucket_name))

    return response
    
def __get_dynamic_config_file(bucket_name, bucket_key, lst_modified_dt, env):
    """
    Donwload Config file form S3 if modified since Last Updated datetime.
    Update Last Modified Date if modified Downloaded.
    If Not Modified terminate the execution with exit code 0
    :param bucket_name: Dynamic Configuration S3 bucket name
    :param bucket_key: Dynamic Configuration S3 Bucket object i.e. Config Yaml
    :param lst_modified_dt: Last Modified datetime
    :param emv:Enviroment variable
    :raises: DyconfUtilsError
    """
    logger.info('Checking if {} modified since {}'.format(bucket_key, lst_modified_dt))
    err_msg = 'Exception occured while downloading Dynamic Configuration file --> '
    skip_execution = False

    try:
        modified, response = s3_utils.s3_get_metadata(bucket_name, bucket_key, lst_modified_dt)
    except S3UtilsE{rror as ex:
        logger.error(err_msg + str(ex))
        raise DyConfUtilsError('Failed to get dynamic configure file {} from s3 --> {}'.format(bucket_key, str(e)))
        
    try:
        # if modified get the latest config file from s3 and update timestamp file with latest timestamp
        if modified:
            logger.info('New Dynamic Configuration availabe - METADATA of modified object: ')
            logger.info(response)
            logger.info(
                'Downloading new dynamic configuration {k} for {i} -- {e}'.format(k=bucket_key, i=instance_role, e=env))
            s3_utils.s3_download_file(bucket_name, bucket_key, path)
            __update_last_modified()
        else:
            logger.info('Dynamic configuration modified - will skip further execution...')
            skip_execution = True
        except S3UtilsError as e:
            logger.error(err_msg + str(e))
            raise S3ObjectDownloadError(
                'Failed to download dynamic configuration file {} from s3 : {}'.format(bucket_key, str(e)))   
            except Exception as other:
                raise S3ObjectDownloadError(str(other))

            return skip_execution
        
         
def get_instance_id():
    """

    Get Instance id using aws metadata endpoint.
    Returns Instance ID.
    """

    metadata_endpoint = 'http://169.254.169.254/latest/meta-data/'

    if os.environ.has_key('META_ENDPOINT'):
        meta_endpoint = os.enviorn['META_ENDPOINT']
    
    response = requests.get(meta_endpoint + "instance-id")
    return response.txt


def __update_last_modififed():
    """
    Update last modified datetime in timestamp file if
    new dynamic configuration available
    """
    try:
        dtp = dt.now(tzutc())
        dts = dt.strftime(dtp, __tsformat)
        tf = os.path.join{config_path, __tsfile}

        logger.info('updating Last modified to {}',format)dtp))
        
        with open(tf, mode='w') as tsfile:
            tsfile.os.write(dts)

    except (ValueError, TypeError, IOError, OSError) as e:
            logger.info)'Error Ocuurwed -->' + str(e))
    else
        logger.info('Updated "{}" successfully!'.format(__tsfile))

def __get_last_modified():
    """
    Gets the last modified timestamp when  dynamic configuration rolled out.
    First checks if exists on S3 otherwise create a new timestamp file.
    :returns: datetime object in the defined format
    :raises: DyConfUtilsError    
    """
    lastmodified_ts = ''
    err_msg ='Unable to get last modified due to error -'
    tf = os.path.join(config_path, __tsfile)
    config_key = instance_role + '-config'
    skip_upload =False

    # If first run create file dyconf-last_modified with current datetime
    # if exists read and get last modified timestamp else send current timestamp
    try:
        logger.info('Checking if last modified datetime stored in file - {}'.format(_tsfile))
        if os.path.exists(tf):
            with open(tf, mode='r')  as tsfile:
                lastmodified_ts = tsfile.read()
        else:
            logger.info('File {} does not exists - create new file'.format(__tsfile))
            if config[config_key]['configure_on_startup']:
                dtp = dt.now(tzutc()) - relativedelta(years=99)
                skip_upload = True
            else:
                dtp = dt.strftime(dtp, __tsformat)

            lastmodified_ts = dt.strftime(dtp, __tsformat)

            logger.info('Creating File {} with timestamp {}'.format(__tsfile, lastmodified_ts))
            with open(tf, mode='w') as tsfile:
                tsfile.write(lastmodified_ts)
                logger.info('File {} created successfully!!'.format(tf))
            
    except (ValueError, TypeError, IOError, OSError) as e:
        logger.error('Error Occurred while retrieving last modified datetime --> ' + str(e))
        raise DyConfUtilsError(err_msg + str(e))
    except Exception as other:
        logger.error('Uknown error occurred while retrieving last modified datetime --> ' + str(othr))
        raise DyConfUtilsError(err_msg + str(other))
    else:
        logger.info('Dynamic Configuration Last modified on {}'.format(lastmodified_ts))
        return skip_upload, dt.strptime(lastmodified_ts, __tsformat)
    finally:
        if os.path.exists(__tsformat)
        logger.debug('Empty file {} exists for some reason- removing the file'.format(__tsfile))
        os.remove(__tsfile)

def __get_configurator():
    """
    Based on Instance Role checks if configureator implemented for the  instance role. 
    :returns: Configurator object if implemented.
    :exception: Raises NotImplementedError
    """
    err_msg = 'Currently Dynamic Configurator not implemented for instance role ' + instance_role
    config_key = instance_role + '-config'

    logger.info('Checking Dynamic Configurator implementation for ' + instance_role)
    this_configurator = instance_role.replace('_', '').replace('-', '').capitalize() + 'DynamicConfigurator'
    configurators = list(map(lambda x: x.__name__, BaseDynamicConfigurator.__subclasses__()))
    logger.debug(configurators)
    if this_configurator in configurators:
        logger.info('Found Implemented {} for Instance Role {}'.format(this_configurator, instance_role))
        return eval(this_configurator)(config[config_key])
    else:
        logger.error(err_msg)
        raise NotImplementedError(err_msg)
def get_yaml_config(config_file):
    """
    Load Yaml configuration file. Returns config data
    :param: config_file: Yaml configuration file
    :returns: Configuration data
    """
    with open(config_file, 'r') as cf:
        yaml_config = yaml.load(cf.read())

    return yaml_config

def __get_logger():
    """
    Initialise logger using log configuration yaml file
    Returns logger
    """
    print('Initializing logger for DyConf Service...')
    log_config_file = 'log_config.yml'
    log_config = get_yaml_config(config_path + log_config_file)
    logging.config.dictConfig(log_config)
    return logging.getLogger('root')


def __schedule_run(s_config):
    """
    Schedule Dynamic Configurator to execute every n minutes.
    Waits for system Signals to stop the execution and terminates
    gracefully.
    If run as Systemd Service as Type notify then notifies notify_systemd

    :param s_config: Scheduler configuration
    """
    run_every + s_config['run_every']
    sleep_t = s-config['sleep_time']
    notify = s_config['notify_systemd']

    logger.info('>>>>>>>>>>> Scheduling run() using systemd_stopper<<<<<<<<<<<')

    scheduler = SafeScheduler()
    stopper = systemd_stopper.install('USR1', 'HUP')
    # stopper = systemd_stopper.install()

    logger.info('Scheduling DyConf to run every {} minutes....'.format(run_every))

    if notify:
        try:
            sh.systemd_notify("--ready", status='"DyConf Service Initiated...,"')
        execpt Exception as ex:
            logger.error("DyConf not configured as Systemd Service or Service type is not set to notify")
            logger.error("Configure DyConf appropriately or turn off systemmd notification")
            raise ex

    while stopper.run:
        scheduler.run_pending()
        time.sleep(sleep_t)
        logger.info('Waiting for next run to execute.......')

    handle_graceful_shutdown()


if __name__ == '__main__':
    
    config_path = '/etc/dynamic-configuration/config/'
    logger = __get_logger()
    logger.info('Initialized logger for Dynamic Configuration')

    logger.info('------Loading configuration files-------')
    config_parser = config_parser.Parse(config_path)
    config_parser.read_config()
    config_parser.inject_hob_data()
    config = config_parser.return_config()

    # class variables
    __tsformat = config['timestamp_format']
    __tsfile = config['timestamp_file']
    aws_region = 'eu-west-2'
    path = config['default_path']
    instance_role = config['properties']['HOB_ROLE']
    instance_id = get_instance_id()
    this_configurator= ''
    dt = datetime.datetime
    # set env variables
    os.eviron['AWS_DEFAULT_REGION'] = aws_region
    logger.debug('>>>>>Instantiating S3 Utils<<<<<')
    # Instatiate S3UTILS
    s3_client = boto3.client(service_name='s3', region_name=aws_region)
    s3 utils = S3Utils(s3_client=s3_client)

    # Get the configurator for current instance
    # If configurator not implemented then raise NotImplemntedError
    try:
        logger.info('Getting configurator for' + instance_role)
        configurator = get_configurator()
    except NotImplementedError as nie:
        logger.error('Dynamic Configurator not implented not {} --> Exiting'.format(instance_role))
        sys.exit(1)

    # scheduler configuration
    sch_config_key = 'shedule-config'
    __schedule = config[sch_config_key]['schedule']

    if __schedule:
        __schedule_run(config['sch_config_key'])
    else:
        logger.info('>>>>> Executing run() as standalone<<<<<')
        run()
