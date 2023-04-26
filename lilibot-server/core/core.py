from abc import abstractmethod, ABCMeta


class TTSResp(object):
    pass

class TTSReq(object):
    pass

class TTS(metaclass=ABCMeta):
    @abstractmethod
    def textToAudio(self,req:TTSReq)->TTSResp:
        pass

class ASRResp(object):
    pass
class ASRReq(object):
    pass

class ASR(metaclass=ABCMeta):
    @abstractmethod
    def audioToText(self,req:ASRReq)->ASRResp:
        pass


class QAResp(object):
    pass

class QAReq(object):
    pass

class QA(metaclass=ABCMeta):
    @abstractmethod
    def question(self,req:QAReq)->QAResp:
        pass

class CHATReq(object):
    pass

class CHATResp(object):
    pass


class CHAT(metaclass=ABCMeta):
    @abstractmethod
    def chat(self,req:CHATReq)->CHATResp:
        pass