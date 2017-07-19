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
import shlex
import time
from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
    FileTransferSpeed, FormatLabel, Percentage, \
    ProgressBar, ReverseBar, RotatingMarker, \
    SimpleProgress, Timer, UnknownLength


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
            printer.out("Getting all deployments for [" + self.login + "] ...")
            deployments = self.api.Users(self.login).Deployments.Getall()
            deployments = deployments.deployments.deployment

            if deployments is None or len(deployments) == 0:
                printer.out("No deployment available")
            else:
                printer.out("Deployments:")
                table = Texttable(800)
                table.set_cols_dtype(["t", "t", "t", "t", "t", "t"])
                table.header(
                    ["Deployment name", "Deployment ID", "Hostname", "Region", "Source used", "Status"])
                deployments = generics_utils.order_list_object_by(deployments, "name")
                for deployment in deployments:
                    deployment_id = deployment.applicationId
                    deployment_status = deployment.state
                    instances = deployment.instances.instance
                    instance = instances[-1]
                    if instance.scanSummary:
                        source = "Scan ID: " + str(extract_scannedinstance_id(instance.scanSummary.uri))
                    elif instance.applianceSummary:
                        source = "Stack ID: " + str(generics_utils.extract_id(instance.applianceSummary.uri))
                    else:
                        source = str(None)
                    if instance and instance.location and instance.hostname:
                        table.add_row([deployment.name, deployment_id, instance.hostname, instance.location.provider, source, deployment_status])
                    else:
                        table.add_row([deployment.name, deployment_id, None, None, source, deployment_status])
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

    def arg_terminate(self):
        doParser = ArgumentParser(prog=self.cmd_name + " terminate", add_help=True,
                                  description="Terminate a deployment")
        mandatory = doParser.add_argument_group("mandatory arguments")
        mandatory.add_argument('--id', dest='id', required=True,
                               help="id of the deployment to terminate")
        optional = doParser.add_argument_group("optional arguments")
        optional.add_argument('--force', '-f', dest='force', required=False, action='store_true', help='Terminate the deployment without asking for confirmation')
        return doParser

    def do_terminate(self, args):
        try:
            # add arguments
            doParser = self.arg_terminate()
            doArgs = doParser.parse_args(shlex.split(args))

            deployment = self.api.Users(self.login).Deployments(doArgs.id).Get()
            if (not doArgs.force and generics_utils.query_yes_no("Do you really want to delete deployment with id '" + str(doArgs.id) + "' named '" + deployment.name + "'")) or doArgs.force:
                # When terminating a running deployment, we stop if the status goes to on-fire.
                # But when terminating an on-fire deployment we stop if it is terminated.
                # So we need to get the status before invoking the terminate.
                status = self.api.Users(self.login).Deployments(doArgs.id).Status.Getdeploystatus()
                self.api.Users(self.login).Deployments(doArgs.id).Terminate()
                printer.out("Deployment is stopping")
                bar = ProgressBar(widgets=[BouncingBar()], maxval=UnknownLength)
                bar.start()
                i = 1
                while (self.deployment_exists(doArgs.id)):
                    if status.message != "on-fire":
                        status = self.api.Users(self.login).Deployments(doArgs.id).Status.Getdeploystatus()
                        if status.message == "on-fire":
                            break
                    time.sleep(1)
                    bar.update(i)
                    i += 2
                bar.finish()

                if self.deployment_exists(doArgs.id):
                    printer.out("Could not terminate the deployment.", printer.ERROR)
                    if status.message == "on-fire" and status.detailedError:
                        printer.out(status.detailedErrorMsg, printer.ERROR)
                    return 1
                else:
                    printer.out("Deployment terminated", printer.OK)

            return 0
        except ArgumentParserError as e:
            printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
            self.help_terminate()
        except Exception as e:
            return handle_uforge_exception(e)

    def help_terminate(self):
        doParser = self.arg_terminate()
        doParser.print_help()

    def deployment_exists(self, searched_deploy_id):
        deployments = self.api.Users(self.login).Deployments.Getall()
        deployments = deployments.deployments.deployment

        if deployments is None or len(deployments) == 0:
            return False
        else:
            for deployment in deployments:
                deployment_id = deployment.applicationId
                if deployment_id == searched_deploy_id:
                    return True
        return False
