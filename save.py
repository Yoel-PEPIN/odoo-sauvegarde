
        lg = logging.getLogger()
        lg.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

        # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
        # file_handler = RotatingFileHandler('logs/' + datetime.now().strftime("%Y%m%d-%H-%M-%S") + '.log', 'a', 1000000, 1)
        file_handler = RotatingFileHandler('logs/' + datetime.now().strftime("%Y%m%d-%H-%M-%S") + '.log', 'a', 1000000,
                                           1)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        lg.addHandler(file_handler)

        lg.info('Start Log')

        d = datetime.today() - timedelta(days=7)
        for file in glob.glob("logs/" + str(d.strftime("%Y%m%d")) + "*"):
            lg.info(file + ' removed')
            os.remove(file)

        if not os.path.isdir('temp'):
            os.mkdir('temp')

        if os.path.isdir('filestore'):
            tf = tarfile.open("temp/sample.tar.gz", mode="w:gz")
            for file in glob.glob("filestore/*"):
                lg.info(file + ' compressed')
                tf.add(file)

            tf.close()
        else:
            lg.error('No Filestore !')