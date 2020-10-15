---
id: sparrow-on-windows
title: Sparrow on Windows
sidebar_label: Sparrow on Windows
---

### Docker for Windows:

Sparrow relies on [Docker](https://www.docker.com/) to install dependencies and to build an instance of sparrow on a local machine. Docker was designed for MacOS and Linux based operating systems but can now also work on a Windows based operating system.
(_[Docker for Winodws](https://docs.docker.com/docker-for-windows/install/)_)

Right away there are some system prerequisites for using Docker in Windows. First, you must have either Windows Pro, Education or Enterprise. If you have Windows Home you will **NOT** be able to download and run Docker or Sparrow at this time. This is because, the Windows solution for running Docker depends on using [WSL 2](https://docs.microsoft.com/en-us/windows/wsl/install-win10) (Windows Subsystem for Linux v2) and [Hyper-V](https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/about/) to create a virtual environment to run Linux on. Your machine also needs to have a 64-bit processor and at least 4 GB of RAM.

The first step to running Docker on a Windows Operating system is getting WSL 2 running. Directions for setting up WSL 2 can be found [here](https://docs.microsoft.com/en-us/windows/wsl/install-win10). Some of the main points are:

- Updating your version of Windows to the most recent (2004 version, build 1904 or higher).
- Download WSL version 1
- Enable Hyper V by following [these directions ](https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/quick-start/enable-hyper-v)
- Update WSL 1 to WSL 2
- Download a linux distribution of your choice, like Ubuntu
- Set WSL 2 as your default distributor

Once WSL 2 is installed you are now ready to download [Docker for Windows](https://docs.docker.com/docker-for-windows/install/). After docker has successfull installed you can begin the process of cloning the sparrow repository to your local git repository. **THIS IS THE MOST IMPORTANT PART**. The largest hurdle that we had in getting Sparrow to run on a Windows computer, we believe, was caused during the git clone of the Sparrow repository.

The issue is because of the difference in line endings between Windows and Linux operating systems. Line endings tell an operating system when a line in a file is over. In Linux based systems, the end of a line is noted by LF line endings. In Windows, CRLF is used to note line endings. Docker, being run in a Linux kernal, will recognize LF line endings; however, when you clone the repository using git clone on a Windows computer it may automatically switch the line endings to CRLF which will be **UNREADABLE** to docker and will result in errors saying `No such file or directory`.

**TO FIX** you can simply add `--config core.autocrlf=input` after the repository name on the git command line during cloning. For instance:
`git clone <repoNameHere> --config core.autocrlf=input`.
After you have cloned the repository make sure your line endings are LF in your code editory before trying to get sparrow to run. If you feel comfortable with everything being set. You can continue to the [getting started](https://sparrow-data.org/docs/getting-started) part of the documentation.

There **MAY** be a way to download Docker on Windows Home. **NOTE** we have not tried this way so we are not assured of its validity.

Instead of Hyper-V, enable Virtual Machine Platform in Windows Features. This will act the same as Hyper-V setting up a virtual environment to run WSL 2 in.
