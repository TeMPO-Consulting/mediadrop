# This is a Dockerfile to create a Axitube Environment on Debian 7.0 64 bits
#
# root password:    axitube
# docker user:      docker
# docker password:  docker
# psql user:        docker
# psqlpassword:     docker
#
# VERSION 0.0

# use Debian 7.0 image provided by docker.io
FROM debian:wheezy

MAINTAINER Quentin THEURET, qt@tempo-consulting.fr

# Get noninteractive frontend for Debian to avoid some problems:
#    debconf: unable to initialize frontend: Dialog
ENV DEBIAN_FRONTEND noninteractive

# Set the locale
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US:en

RUN apt-get update; \
 apt-get upgrade -y

# Install postgresql, ssh server (access to the container), supervisord (to launch services), 
#+ tmux (to not open a lot of ssh connections), zsh and vim (to work into the container),
#+ bzr and python-argparse (for MKDB script), ipython (for a better Python console)
RUN apt-get install -y openssh-server supervisor screen tmux zsh vim bzr python-argparse ipython mysql-server git bash
RUN apt-get install -y python-dev libmysqlclient-dev

# CONFIGURATION
RUN mkdir -p /var/run/sshd
RUN mkdir -p /var/log/supervisor
RUN echo 'root:axitube' |chpasswd # change default root password

# Add special user docker
RUN useradd -m docker # create the home directory (-m option)
RUN echo "docker:docker" | chpasswd # change default docker password
# Permit docker user to user tmux
RUN gpasswd -a docker utmp
# Change docker user default shell
#RUN chsh -s /usr/bin/zsh docker
RUN chsh -s /bin/bash docker

# Add Axitube dependancies
RUN apt-get install -y python-virtualenv

USER docker
#RUN cd /home/docker && virtualenv --distribute --no-site-packages axitube-env
#RUN git clone https://github.com/TeMPO-Consulting/mediadrop axitube
#RUN cd axitube
#RUN ../axitube-env/bin/activate && python setup.py develop

ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf
# Add tmux configuration for docker user
ADD tmux.conf /home/docker/.tmux.conf
# Add zsh configuration for docker user
ADD bashrc /home/docker/.bashrc

# Open some ports: 22(SSH), 5432(POSTGRESQL), 8061(OpenERP Web Client)
EXPOSE 22 5432 8061

# Add VOLUMEs to allow backup of config, logs and databases
VOLUME  ["/etc/mysql", "/var/log/mysql", "/var/lib/mysql"]

# Gain root permission
USER root

# Launch supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
