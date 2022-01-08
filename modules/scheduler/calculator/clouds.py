class Clouds:

    def __init__(self, config):
        self.config = config

    def cloudiness(self, clouds):
        avg_clouds = sum(cloud for cloud in clouds) / len(clouds)
        return 1 - avg_clouds / 100