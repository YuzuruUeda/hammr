# Copyright 2007-2015 UShareSoft SAS, All rights reserved
#
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from ussclicore.utils import generics_utils, printer, progressbar_widget, download_utils
from hammr.utils import *
from uforge.objects.uforge import *
from hammr.utils.hammr_utils import *

class Deploy(Cmd, CoreGlobal):
    """Displays all the deployments and instances information"""
    cmd_name = "deploy"
    pbar = None

    def __init__(self):
        super(Deploy, self).__init__()

    def arg_list(self):
        doParser = ArgumentParser(prog=self.cmd_name + " list", add_help=True,
                                  description="Displays all the deployments and instances information")
        return doParser

    def do_list(self, args):
        try:
            printer.out("Getting all deployments [" + self.login + "] ...")
            deployments = self.api.Users(self.login).Deployments.Getall()
            deployments = deployments.deployments.deployment

            if deployments is None or len(deployments) == 0:
                printer.out("No deployment available")
            else:
                printer.out("Deployments:")
                table = Texttable(800)
                table.set_cols_dtype(["t", "t", "t", "t", "t"])
                table.header(
                    ["Deployment name", "Deployment ID", "Hostname", "Region", "Status"])
                deployments = generics_utils.order_list_object_by(deployments, "name")
                for deployment in deployments:
                    deployment_id = deployment.applicationId
                    deployment_status = self.api.Users(self.login).Deployments(deployment_id).Status.Getdeploystatus()
                    deployment_status = deployment_status.message
                    instances = deployment.instances.instance
                    instance = instances[-1]
                    if instance and instance.location and instance.hostname:
                        table.add_row([deployment.name, deployment_id, instance.hostname, instance.location.provider, deployment_status])
                    else:
                        table.add_row([deployment.name, deployment_id, None, None, deployment_status])
                print table.draw() + "\n"
                printer.out("Found " + str(len(deployments)) + " deployments")

            return 0
        except ArgumentParserError as e:
            printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
            self.help_list()
        except Exception as e:
            return handle_uforge_exception(e)

    def help_list(self):
        doParser = self.arg_list()
        doParser.print_help()

