from dirsync.infra.ui import cli

if __name__ == "__main__":
    try:
        cli.execute()
    except KeyboardInterrupt:
        pass
