from datetime import datetime
import pytest
import paramiko
from logger import logger


class TestVMConfig:
    """
    To Test the Virtual box VM configuration.
    """
    HOST = "192.168.56.101"
    USERNAME = "geetanjali"
    PASSWORD = "Testvm@123"

    @pytest.fixture
    def to_access_vm_from_virtual_box(self):
        """
        To access the VM created in Virtual box.
        :return:
        """
        client = paramiko.client.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.HOST, username=self.USERNAME,
                       password=self.PASSWORD)
        return client

    @pytest.mark.cli
    def test_check_cpu_idle_of_vm(self, to_access_vm_from_virtual_box):
        """
        To test the CPU idle of a given VM
        :param to_access_vm_from_virtual_box:
        :return:
        """
        cmd = "mpstat 1 5 | awk 'END{print $12}'"
        _, stdout, _ = to_access_vm_from_virtual_box.exec_command(
            cmd)
        cpu_idle = stdout.readlines()
        cpu_idle_percent = (cpu_idle[0]).split('\n')
        file = open('reports/vm_config.txt', 'w')
        current_time = datetime.now()
        dt_string = current_time.strftime("%d/%m/%Y %H:%M:%S")
        file.write(dt_string)
        file.write(''.join(' CPU Idle  in % ='))
        file.write(' '.join(str(cpu_idle_percent[0])))
        file.write(''.join('\n'))

        logger.info(
            "Checking CPU idle on host {} VM is {}".format(self.USERNAME,
                                                           float(
                                                               cpu_idle_percent[
                                                                   0])))
        assert float(cpu_idle_percent[0]) >= 10.00

    cmd = ["df /dev/sda1 | awk 'END{print $5}'",
           "df /dev/sda5 | awk 'END{print $5}'",
           "df /dev/loop1 | awk 'END{print $5}'"]

    @pytest.mark.cli
    @pytest.mark.parametrize("cmd", cmd)
    @pytest.mark.xfail(reason="TC's should be fail when usgae is grater than 90%")
    def test_check_disk_usage_on_vm(self, cmd, to_access_vm_from_virtual_box):
        """
        To test that the disk usage on a given disk host is less than 90%.
        :param cmd:
        :param to_access_vm_from_virtual_box:
        :return:
        """
        _, stdout, _ = to_access_vm_from_virtual_box.exec_command(cmd)
        disk_usage_op = stdout.readlines()
        disk_usage = disk_usage_op[0].split('%')
        file = open('reports/vm_config.txt', 'a')
        current_time = datetime.now()
        dt_string = current_time.strftime("%d/%m/%Y %H:%M:%S")
        file.write(dt_string)
        disk_name = ((cmd.split('|'))[0].split('df'))[1]
        file.write(''.join(' disk usage on {}in % ='.format(disk_name)))
        file.write(' '.join(disk_usage[0]))
        file.write(' '.join('\n'))
        logger.info(
            "Checking disk used on host {} VM is{}".format(self.USERNAME,
                                                           disk_usage[0]))
        assert int(disk_usage[0]) < 90

    @pytest.mark.cli
    def test_check_ram_usage_on_vm(self, to_access_vm_from_virtual_box):
        """
        To test that the memory utilization on a vm is less than 90 %.
        :param to_access_vm_from_virtual_box:
        :return:
        """

        _, stdout, _ = to_access_vm_from_virtual_box.exec_command(
            "free -t | awk 'END{print $3/$2*100}'")
        mem_usage_op = stdout.readlines()
        mem_usage = (mem_usage_op[0]).split('\n')
        logger.info("Checking memory Utilization on host {} VM is {}".format(
            self.USERNAME, [mem_usage[0]]))
        file = open('reports/vm_config.txt', 'a')
        current_time = datetime.now()
        dt_string = current_time.strftime("%d/%m/%Y %H:%M:%S")
        file.write(dt_string)
        file.write(''.join(" Memory Utilization in % ="))
        file.write(' '.join(mem_usage))
        file.write(''.join('\n'))
        file.close()
        assert float(mem_usage[0]) < 90
