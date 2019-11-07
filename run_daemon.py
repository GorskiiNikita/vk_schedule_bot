import daemon

from vk_main import main

with daemon.DaemonContext():
    main()