class RENDER_STATISTICS:
    def __init__(self,name,row,*flags):
        self.flagName = name
        self.data = []
        self.displayFlag = False
        self.row = row
        self.associated_flags = flags

    def calculate_avg(self):
        print self.data
        if self.data:
            total_sum = 0
            for val in self.data:
                total_sum += val
            return total_sum / len(self.data)

    def get_max(self):
        return max(self.data)

    def reset_data(self):
        self.data[:] = ""
