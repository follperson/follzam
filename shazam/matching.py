from database_management import DatabaseHandler
from signal_processing import SignalProcessor
# should i not do this in a class so I can multithread it? or is that not necessary


class SignatureChecking(object):
    """
        This object is dedicated to housing comparison functions for signatures
        flexible to use multiple types of signatures

    """
    def __init__(self, reference,
                 n_matches=1,
                 signature_type=SignalProcessor.SignatureProcesses.EXACT_MATCH):
        """

        :param reference:
        :param n_matches:
        :param signature_type:
        """
        assert n_matches > 0
        assert signature_type in SignalProcessor.SignatureProcesses.ALL
        self.reference = reference
        self.target_distance = {}

    def compare(self, target):
        """
            compare the distance between the the self.reference signature and the target
        :param target:
        :return:
        """
        # compute distance
        return 'distance'

    def compare_multiple(self, targets):
        for target in targets:
            distance = self.compare(target)
            self.target_distance[target] = distance




def compare_new_signature(new_sig, num_matches):
    dbh = DatabaseHandler()
    signatures = dbh.get_all_signatures()
    sc = SignatureChecking(new_sig, num_matches, 'signaturetype')
    sc.compare_multiple(signatures)
    return min(sc.target_distance.keys(), key=lambda x: sc.target_distance[x])






