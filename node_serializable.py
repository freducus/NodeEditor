class Serializable():
    def __init__(self):
        self.id = id(self)

    def serialize(self):
        raise NotImplemented

    def deserialize(self, data, hashmap={}, restore_id=True):
        raise NotImplemented
