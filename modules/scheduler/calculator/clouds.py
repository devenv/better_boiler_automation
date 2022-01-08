class Clouds:

    def __init__(self, config):
        self.config = config

    def cloudiness(self, clouds):
        avg_clouds = sum(cloud for cloud in clouds) / len(clouds)
        return avg_clouds / 100