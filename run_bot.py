import daemon
import os
from vk_main import main

here = os.path.dirname(os.path.abspath(__file__))
err = open('err.log', 'a+')


with daemon.DaemonContext(working_directory=here, stderr=err):
    main()
