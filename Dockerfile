FROM dind
MAINTAINER Paddy Carey <paddy@wackwack.co.uk>

# no tty
ENV DEBIAN_FRONTEND noninteractive

# get up to date
RUN apt-get update --fix-missing
RUN apt-get upgrade -y

# install packages from apt
RUN apt-get install -y git
RUN apt-get install -y python-dev
RUN apt-get install -y python-pip
RUN apt-get install -y python-requests

# install any pypi dependencies (prefer installing from apt when possible)
RUN pip install fabric
RUN pip install "sheep>=0.3.11"

# copy required files into the image
ADD app/ /app/
ADD secrets/gitlab/local-key.pem /root/.ssh/id_rsa
RUN chmod 0600 /root/.ssh/id_rsa
ADD secrets/gitlab/local_known_hosts /root/.ssh/known_hosts
ADD secrets/conf/local.conf /app.conf

# Install the magic wrapper.
ADD scripts/wrapdocker /usr/local/bin/wrapdocker
RUN chmod +x /usr/local/bin/wrapdocker

# get the ip address of the host as exposed inside the container
RUN /sbin/ip route|awk '/default/ { print $3 }' > /etc/host_ip

# default run command
CMD wrapdocker
