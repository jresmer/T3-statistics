from dao import DAO
from math import log10, sqrt, pow, log


ERRO = 0.00000001
class EmpiricModel:
    
    def __init__(self, data: list) -> None:
        # Sturges
        self.k = round(1 + 3.322*log10(len(data)))
        # classification
        upper_bound = max((p["price"] for p in data)) + ERRO
        lower_bound = min((p["price"] for p in data)) - ERRO

        price_range = upper_bound - lower_bound
        step = price_range / self.k

        classes = [None] * self.k
        current_price = lower_bound
        l = len(data)

        avg = 0
        for i in range(self.k):

            classes[i] = list()
            j = 0
            while j < len(data):
                
                if data[j]["price"] >= current_price and data[j]["price"] < current_price + step:
                    data[j]["range"] = (current_price, current_price + step)
                    classes[i].append(data[j])
                    avg += data[j]["price"]
                    data.pop(j)
                    continue

                j += 1
            current_price += step

        self.classes = classes
        self.class_frequencies = [None] * self.k
        self.class_percentages = [None] * self.k
        self.X = [None] * self.k
        self.metrics = dict()
        self.grouped_metrics = dict()
        c = 1 / l
        c1 = 1 / (l - 1)
        avg *= c
        self.metrics["Average"] = avg
        counting = dict()
        gp_avg = 0
        for i, ki in enumerate(classes):

            self.class_percentages[i] = len(ki) * c
            self.class_frequencies[i] = len(ki)
            self.X[i] = (ki[0]["range"][0] + ki[0]["range"][1]) * 0.5
            gp_avg += self.X[i] * len(ki) / l
            for ind in ki:
                if ind["price"] not in counting.keys():
                    counting[ind["price"]] = 0
                counting[ind["price"]] += 1
        # determining mode
        max_occur = max((ind for ind in counting.values()))
        mode = list(key for key in counting.keys() if counting[key] == max_occur)
        sum_ = mode[0]
        if len(mode) > 1:
            for v in mode[1:]:
                sum_ += v
            sum_ = sum_ / len(mode)
        self.metrics["Mode"] = sum_
        # determining median
        prices = list(counting.keys())
        prices.sort()
        length = len(prices)
        half_len = length // 2
        if length % 2:
            median = (prices[half_len] + prices[half_len+1]) / 2
        else:
            median = prices[half_len]
        self.metrics["Median"] = median
        # determining var
        var = 0
        for price in prices:
            var += pow(avg - price, 2)
        self.metrics["Var"] = var * c1
        # determining sd
        self.metrics["Standard Deviation"] = sqrt(self.metrics["Var"])
        # determining CV
        self.metrics["CV"] = self.metrics["Standard Deviation"] / self.metrics["Average"]
        # determining assymetries
        self.metrics["MoAssymmetry"] = (self.metrics["Average"] - self.metrics["Mode"]) / self.metrics["Standard Deviation"]
        self.metrics["MdAssymmetry"] = (self.metrics["Average"] - self.metrics["Median"]) / self.metrics["Standard Deviation"]
        # determining grouped average
        self.grouped_metrics["Average"] = gp_avg
        # determining grouped median
        total_perc = 0
        F = 0
        i = 0
        for i in range(len(classes)):

            F = total_perc
            total_perc += self.class_percentages[i]
            if total_perc >= 0.5:
                break
        l = classes[i][0]["range"][0]
        h = step
        f = self.class_frequencies[i]
        self.grouped_metrics["Median"] = l + h*(0.5-F)/f
        # determining grouped mode
        mode_gp = max(self.class_percentages)
        self.grouped_metrics["Mode"] = self.X[self.class_percentages.index(mode_gp)]
        # determining grouped var
        var = 0
        for i in range(len(classes)):

            var += pow(self.grouped_metrics["Average"] - self.X[i], 2) * self.class_percentages[i]
        self.grouped_metrics["Var"] = var
        # determining grouped sd
        self.grouped_metrics["Standard Deviation"] = sqrt(self.grouped_metrics["Var"])
        # grouped CV
        self.grouped_metrics["CV"] = self.grouped_metrics["Standard Deviation"] / self.grouped_metrics["Average"]
        # determining assymetries
        self.grouped_metrics["MoAssymmetry"] = (self.grouped_metrics["Average"] - self.grouped_metrics["Mode"]) / self.grouped_metrics["Standard Deviation"]
        self.grouped_metrics["MdAssymmetry"] = (self.grouped_metrics["Average"] - self.grouped_metrics["Median"]) / self.grouped_metrics["Standard Deviation"]
        # determining errors
        self.errors = dict()
        for key in self.metrics.keys():

            self.errors[key] = abs(self.metrics[key] - self.grouped_metrics[key]) / self.metrics[key]
        # adherence test Zs
        for Ki in self.classes:
            
            Lii, Lsi = Ki[0]["range"]
            Ki[0]["z1"] = (Lii - self.grouped_metrics["Average"]) / self.grouped_metrics["Standard Deviation"]
            Ki[0]["z2"] = (Lsi - self.grouped_metrics["Average"]) / self.grouped_metrics["Standard Deviation"]
        # lognormal
        avg_ = self.grouped_metrics["Average"]
        var = self.grouped_metrics["Var"]
        avg = log(pow(avg_, 2)/sqrt(pow(avg_,2) + pow(var, 2)))
        var = log(1 + pow(var, 2)/pow(avg_, 2))
        sd = sqrt(var)

        for Ki in self.classes:
            
            Lii, Lsi = Ki[0]["range"]
            z1 = (log(Lii) - avg) / sd
            z2 = (log(Lsi) - avg) / sd
            print(f"range = {Lii} |--- {Lsi}")
            print(f"z1 = {z1}, z2 = {z2}")
        print()
    
    def print_metrics(self) -> None:

        sum_of_weights = 0
        for i, Ki in enumerate(self.classes):

            sum_of_weights += self.class_percentages[i]
            range_ = Ki[0]["range"]
            print(f"Class=k{i+1} | {range_}", end=" ")
            h = ["|"] * self.class_frequencies[i]
            h = "".join(h)
            print(h, end=" ")
            print(f"ni={self.class_frequencies[i]}", end=" ")
            print(f"weight={self.class_percentages[i]}", end=" ")
            print(f"cumulative weight={sum_of_weights}", end=" ")
            print(f"Xi={self.X[i]}")

        print()
        print("Original Metrics x Grouped Metrics")
        for metric in self.metrics.keys():
            
            print(f"{metric}: {self.metrics[metric]}|{self.grouped_metrics[metric]}")

        print()
        print("Errors")
        for metric in self.errors.keys():
            
            print(f"{metric}: {self.errors[metric]}")
        
        print()
        for i, Ki in enumerate(self.classes):

            range_ = Ki[0]["range"]
            z1 = Ki[0]["z1"]
            z2 = Ki[0]["z2"]
            print(f"Class=k{i+1} | {range_}", end=" ")
            print(f"Oi = {self.class_frequencies[i]}", end=" ")
            print(f"z1 = {z1}, z2 = {z2}")


if __name__ == "__main__":

    dao = DAO()
    data = dao.get_all()[0]["PEPSI COLA"]
    model = EmpiricModel(data)
    model.print_metrics()
    print()
    data = dao.get_all()[0]["SUKITA UVA"]
    model1 = EmpiricModel(data)
    model1.print_metrics()
    print()
    
