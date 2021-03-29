---
id: sparrow-on-windows
title: Sparrow on Windows
sidebar_label: Sparrow on Windows
---

### Docker

Sparrow relies on [Docker](https://www.docker.com/) to install dependencies and to build an instance of sparrow on a local machine through docker containers. Docker was designed for MacOS and Linux based operating systems but can now also work on a Windows based operating system
(_[Docker for Winodws](https://docs.docker.com/docker-for-windows/install/)_), but requires the user to run a Linux kernal in a virtual machine.

### Window's Subsystem for Linux (WSL2)

Right away there are some system prerequisites for using Docker in Windows. First, it's recommended to have either Windows Pro, Education or Enterprise. Windows' solution for running Docker depends on using [WSL 2](https://docs.microsoft.com/en-us/windows/wsl/install-win10) (Windows Subsystem for Linux v2) and in order to do this your computer needs the ability to run a virtual machine. [Hyper-V](https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/about/) is the virtual machine that we've used to run WSL 2; however, Hyper-V is only available on Windows Pro, Education, Enterprise.

:::info Windows Home Users
If you have Windows Home you **may** be able to download and run Docker and Sparrow (**NOTE** this is untested). Instead of Hyper-V, enable Virtual Machine Platform in Windows Features. This should act the same as Hyper-V, setting up a virtual environment to run WSL 2 in.
:::

The first step to running Docker on a Windows Operating system is setting up WSL 2. Directions for setting up WSL 2 can be found [here](https://docs.microsoft.com/en-us/windows/wsl/install-win10). Some of the main points are:

- Updating your version of Windows to the most recent release (2004 version, build 1904 or higher)
- Enable Hyper V by following [these directions ](https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/quick-start/enable-hyper-v) **OR** enable Virtual Machine Platfrom by navigating to Windows Features through settings (same as Hyper-V through settings).
- Download or enable [WSL 1](https://docs.microsoft.com/en-us/windows/wsl/install-win10#step-1---enable-the-windows-subsystem-for-linux)
- Update WSL 1 to WSL 2 by downloading the [Linux kernal update](https://docs.microsoft.com/en-us/windows/wsl/install-win10#step-4---download-the-linux-kernel-update-package)
- Set WSL 2 as your [default distributor](https://docs.microsoft.com/en-us/windows/wsl/install-win10#step-5---set-wsl-2-as-your-default-version)
- Download a [linux distribution](https://docs.microsoft.com/en-us/windows/wsl/install-win10#step-6---install-your-linux-distribution-of-choice) of your choice (Ubuntu 20.04 LTS is one we used)

Once WSL 2 is installed you are now ready to download [Docker for Windows](https://docs.docker.com/docker-for-windows/install/). After docker has successfully installed you can begin the process of downloading the [bundled version of sparrow](/docs/getting-started#bundled-version), or, if you are planning to develop the core codebase, cloning the sparrow repository to your local git repository.

:::caution IMPORTANT
One of the largest hurdles that we had in getting Sparrow to run on a Windows computer, was caused during cloning of the Sparrow repository.
:::

### LF vs CRLF Line Ending Errors

The issue is because of the difference in line endings between Windows and Linux operating systems. Line endings tell an operating system when a line in a file is over. In Linux based systems, the end of a line is noted by LF line endings. In Windows, CRLF is used to note line endings. Docker, being run in a Linux kernal, will recognize LF line endings; however, when you clone the repository using git clone on a Windows computer it may automatically switch the line endings to CRLF which will be **UNREADABLE** to the Sparrow container and will result in errors saying `No such file or directory`.

**TO FIX** you can simply add `--config core.autocrlf=input` after the repository name on the git command line during cloning. For instance:
`git clone <repoNameHere> --config core.autocrlf=input`.
After you have cloned the repository make sure your line endings are LF in your code editor before trying to get sparrow to run. If you feel comfortable with everything being set. You can continue to the [getting started](https://sparrow-data.org/docs/getting-started) part of the documentation.

### Helpful Links and Tutorials

- [WSL 2 on Windows Home](https://www.youtube.com/watch?v=_fntjriRe48)
- [WSL 2 with Docker](https://www.youtube.com/watch?v=5RQbdMn04Oc&t)
- [Hyper V on Windows](https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/quick-start/enable-hyper-v)
- [WSL 2](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
