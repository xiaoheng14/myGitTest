# -*- coding: utf-8 -*-

"""
@author: dengweiheng
@function: auto install wordpress
@date: 2017-05-12
@version: 2.0
"""

import os
from functools import wraps
import logging
import logging.handlers
import string
import random


def init_logger(log_file):
    dir_path = os.path.dirname(log_file)
    try:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    except Exception as e:
        pass

    handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=20 * 1024 * 1024, backupCount=10)
    # fmt = '%(message)s'
    fmt = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger_instance = logging.getLogger('logs')
    logger_instance.addHandler(handler)
    logger_instance.setLevel(logging.DEBUG)
    return logger_instance

wordpress_log = init_logger('auto_install_wordpress_log.log')


def check_root():
    if os.geteuid() != 0:
        wordpress_log.info(
            "You need to have root privileges!")
        exit()
    else:
        print "Get Root Privileges!"


def get_rand_char(strlen):
    char = string.digits + string.letters
    s = ''.join([random.choice(char) for _ in range(strlen)])
    return s


def run_shell(command):
    ret = os.system('sudo ' + command)
    if ret == 0:
        return True
    return False


def run_shell_normal(command):
    ret = os.system(command)
    if ret == 0:
        return True
    return False


# find . -maxdepth 1 -name "*.tar.gz"  search the pakges

def decorator_check(bag):
    def handle_func(func):
        wraps(func)

        def handle_args(self, arg=False):
            if run_shell("dpkg -l %s" % bag):
                print "%s already installed!" % bag
                arg=True
            func(self, arg)
        return handle_args
    return handle_func


class Wordpress(object):
    def __init__(self, database, dbuser, dbpwd, title, user, email, pwd,
                 url="http://localhost/wordpress/wp-admin/install.php",
                 wp_ver="wordpress-4.7.4-zh_CN.tar.gz", wp_path="/opt"):
        self.database = database
        self.dbuser = dbuser
        self.dbpassword = dbpwd
        self.wordpress_version = wp_ver
        self.wordpress_path = wp_path
        self.url = url
        self.title = title
        self.user = user
        self.email = email
        self.password = pwd
        self.wordpress_locate = "/var/www/html/wordpress"

    def update(self):
        try:
            if not run_shell('apt-get -y update && apt-get -f install && apt-get -y upgrade'):
                wordpress_log.info("update error")
                exit(1)
        except Exception as e:
            wordpress_log.info(e)
            exit(1)

    @decorator_check("apache2")
    def install_apache2(self, arg=False):
        if arg:
            pass
        else:
            try:
                if not run_shell("apt-get -y install apache2"):
                    wordpress_log.info("install apache2 error")
                    exit(1)
            except Exception as e:
                wordpress_log.info(e)
                exit(1)
        if not run_shell("/etc/init.d/apache2 restart"):
            wordpress_log.info("restart apache2 error")
            exit(1)

    @decorator_check("debconf-utils")
    def install_debconf_utils(self, arg=False):
        if arg:
            pass
        else:
            if not run_shell("apt-get -y install debconf-utils"):
                wordpress_log.info("install debconf-utils error")
                exit(1)

    @decorator_check("mysql-client")
    def install_mysql_client(self, arg=False):
        if arg:
            pass
        else:
            if not run_shell("apt-get -y install mysql-client"):
                wordpress_log.info("install mysql-client error")
                exit(1)

    @decorator_check("mysql-server")
    def install_mysql(self, arg=False):
        if arg:
            self.set_db_pwd()
        else:
            try:
                self.install_debconf_utils()
                command = '''
                echo mysql-server mysql-server/root_password password %s | sudo debconf-set-selections    
                echo mysql-server mysql-server/root_password_again password %s | sudo debconf-set-selections  
                ''' % (self.dbpassword, self.dbpassword)
                if not run_shell(command):
                    wordpress_log.info("set mysql password failed")
                    exit(1)
                if not run_shell("apt-get -y install mysql-server"):
                    wordpress_log.info("install mysql-server error")
                    exit(1)
                self.install_mysql_client()
            except Exception as e:
                wordpress_log.info(e)
                exit(1)

    def set_db_pwd(self):  # if mysql password is none
        try:
            if run_shell('''mysql -uroot -e"show databases;"'''):
                command = '''mysql -uroot -e"SET PASSWORD FOR 'root'@'localhost' = PASSWORD('%s');"''' % self.dbpassword
                if not run_shell(command):
                    wordpress_log.info("set db_password failed")
                    exit(1)
            else:
                wordpress_log.info("maybe the password has been exists")
        except Exception as e:
            wordpress_log.info(e)

    def create_db(self):
        try:
            if not run_shell("mysql -u%s -p%s -e'create database if not exists %s';" % (
            self.dbuser, self.dbpassword, self.database)):
                wordpress_log.info("create db %s error" % self.database)
                exit(1)
        except Exception as e:
            wordpress_log.info(e)
            exit(1)

    @decorator_check("libapache2-mod-php5")
    def install_libapache2_mod_php5(self, arg=False):
        if arg:
            pass
        else:
            if not run_shell("apt-get -y install libapache2-mod-php5"):  # 配置APACHE+PHP
                wordpress_log.info("install libapache2-mod-php5 error")
                exit(1)

    @decorator_check("php5")
    def install_php5(self, arg=False):
        if arg:
            pass
        else:
            try:
                if not run_shell("apt-get -y install php5"):
                    wordpress_log.info("install php5 error")  # 安装PHP5
                    exit(1)
                self.install_libapache2_mod_php5()
                if not run_shell("/etc/init.d/apache2 restart"):  # 重启apache
                    wordpress_log.info("restart apache2 error")
                    exit(1)
            except Exception as e:
                wordpress_log.info(e)
                exit(1)

    @decorator_check("php5-mysql")
    def install_php5_mysql(self, arg=False):
        if arg:
            pass
        else:
            if not run_shell("apt-get -y install php5-mysql"):
                wordpress_log.info("install php5-mysql error")
                exit(1)

    @decorator_check("libapache2-mod-auth-mysql")
    def support_mysql(self, arg=False):
        if arg:
            pass
        else:
            try:
                if not run_shell("apt-get -y install libapache2-mod-auth-mysql"):
                    wordpress_log.info("install libapache2-mod-auth-mysql error")
                    exit(1)
                self.install_php5_mysql()
                if not run_shell("/etc/init.d/apache2 restart"):
                    wordpress_log.info("restart apache2 error")
                    exit(1)
            except Exception as e:
                wordpress_log.info(e)
                exit(1)

    @decorator_check("phpmyadmin")
    def install_phpmyadmin(self, arg=False):
        if arg:
            pass
        else:
            try:
                self.install_debconf_utils()
                command = '''
                echo 'phpmyadmin phpmyadmin/dbconfig-install boolean true' | debconf-set-selections
                echo 'phpmyadmin phpmyadmin/app-password-confirm password %s' | debconf-set-selections
                echo 'phpmyadmin phpmyadmin/mysql/admin-pass password %s' | debconf-set-selections
                echo 'phpmyadmin phpmyadmin/mysql/app-pass password %s' | debconf-set-selections
                echo 'phpmyadmin phpmyadmin/reconfigure-webserver multiselect apache2' | debconf-set-selections''' % (
                    self.dbpassword, self.dbpassword, self.dbpassword
                )
                if not run_shell(command):
                    wordpress_log.info("phpmyadmin set failed")
                    exit(1)
                if not run_shell("apt-get -y install phpmyadmin"):
                    wordpress_log.info("install phpmyadmin error")
                    exit(1)
            except Exception as e:
                wordpress_log.info(e)
                exit(1)
        if not run_shell_normal("cd /var/www/html/ && ln -s -b /usr/share/phpmyadmin"):
            wordpress_log.info("ln -s error")
            exit(1)

    def set_config(self, path):
        try:
            s = open('%s/wordpress/wp-config.php' % path, 'wb')
            with open("%s/wordpress/wp-config-sample.php" % path, "r") as f:
                for line in f:
                    if 'database_name_here' in line:
                        s.write("define('DB_NAME', %s);" % self.database)
                        continue
                    elif 'username_here' in line:
                        s.write("define('DB_USER', %s);" % self.dbuser)
                        continue
                    elif 'password_here' in line:
                        s.write("define('DB_PASSWORD', %s);" % self.dbpassword)
                        continue
                    # line.replace('put your unique phrase here', 'helloworld123456')
                    elif 'AUTH_KEY' in line:
                        key = get_rand_char(30)
                        s.write("define('AUTH_KEY', '%s');\n" % key)
                        continue
                    elif 'SECURE_AUTH_KEY' in line:
                        key = get_rand_char(30)
                        s.write("define('SECURE_AUTH_KEY', '%s');\n" % key)
                        continue
                    elif 'LOGGED_IN_KEY' in line:
                        key = get_rand_char(30)
                        s.write("define('LOGGED_IN_KEY', '%s');\n" % key)
                        continue
                    elif 'NONCE_KEY' in line:
                        key = get_rand_char(30)
                        s.write("define('NONCE_KEY', '%s');\n" % key)
                        continue
                    elif 'AUTH_SALT' in line:
                        key = get_rand_char(30)
                        s.write("define('AUTH_SALT', '%s');\n" % key)
                        continue
                    elif 'SECURE_AUTH_SALT' in line:
                        key = get_rand_char(30)
                        s.write("define('SECURE_AUTH_SALT', '%s');\n" % key)
                        continue
                    elif 'LOGGED_IN_SALT' in line:
                        key = get_rand_char(30)
                        s.write("define('LOGGED_IN_SALT', '%s');\n" % key)
                        continue
                    elif 'NONCE_SALT' in line:
                        key = get_rand_char(30)
                        s.write("define('NONCE_SALT', '%s');\n" % key)
                        continue
                    s.write(line)
            s.close()
        except Exception as e:
            wordpress_log.info(e)
            exit(1)

    @decorator_check("wordpress")
    def install_wordpress(self, arg=False):
        if arg:
            pass
        else:
            wp_path = None
            files = os.listdir(self.wordpress_path)
            if self.wordpress_version in files:
                wp_path = os.path.join(self.wordpress_path, self.wordpress_version)
            else:
                url = 'https://cn.wordpress.org/%s' % self.wordpress_version
                if not run_shell("wget -P %s %s" % (self.wordpress_path, url)):
                    wordpress_log.info("wget wordpress error")
                    exit(1)
                wp_path = os.path.join(self.wordpress_path, self.wordpress_version)
            if not run_shell("tar -zxvf %s -C %s" % (wp_path, self.wordpress_path)):
                wordpress_log.info("tar wordpress error")
                exit(1)
        '''
        得到wordpress文件夹，然后按要求编辑wp-config.php文件，
        主要是提供数据库的名字(如这里的wordpress)，用户名(如root)，密码(如安装mysql时键入的密码)。
        '''
        self.set_config(self.wordpress_path)
        if not run_shell("cp -a %s/wordpress /var/www/html/" % self.wordpress_path):
            wordpress_log.info("cp wordpress to /var/www/html/  error")
            exit(1)

    def auto_install_wp(self):
        try:
            if not run_shell_normal("cd %s" % self.wordpress_path):
                wordpress_log.info("cd wordpress_path error")
            if "wp-cli.phar" in os.listdir(self.wordpress_path):
                pass
            else:
                if not run_shell("curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar"):
                    wordpress_log.info("curl wp-cli.phar faile")
                    exit(1)

            if not run_shell("wp --info --allow-root"):
                if not run_shell("php wp-cli.phar --info --allow-root"):
                    wordpress_log.info("install wp-cli.phar failed")
                    exit(1)
                if not run_shell("chmod +x wp-cli.phar"):
                    wordpress_log.info("chmod +x wp-cli.phar failed")
                    exit(1)
                if not run_shell("sudo mv wp-cli.phar /usr/local/bin/wp && wp --info --allow-root"):
                    wordpress_log.info("mv wp-cli to wp failed")
                    exit(1)

            command = "wp core install --path=%s --url=%s --title=%s --admin_user=%s --admin_email=%s --admin_password=%s --allow-root" \
                      % (self.wordpress_locate, self.url, self.title, self.user, self.email, self.password)
            if not run_shell(command):
                wordpress_log.info("install.php failed")
                exit(1)
        except Exception as e:
            wordpress_log.info(e)
            exit(1)

    def start_install(self):
        check_root()
        # self.update()
        self.install_apache2()
        self.install_mysql()
        self.create_db()
        self.install_php5()
        self.support_mysql()
        self.install_phpmyadmin()
        self.install_wordpress()
        self.auto_install_wp()
        print "Successfully install wordpress, visit http://localhost/wordpress/wp-login.php to login!"

if __name__ == '__main__':
    wordpress = Wordpress("blog", "root", "123456", "hello", "hello", "2846321049@qq.com", "123456")
    wordpress.start_install()
