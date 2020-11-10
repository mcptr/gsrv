import uuid


TYPE_MAP = {cls.__name__: cls for cls in [str, int, uuid.UUID]}


class Router:
    def __init__(self, routing):
        self.routing = routing

    def get(self, path):
        if path in self.routing:
            return (self.routing[path], None)

        params = {}
        chosen_route = None
        parts = path.lstrip("/").split("/")

        for route in self.routing:
            rp = route.lstrip("/").split("/")
            if len(rp) != len(parts):
                continue
            else:
                chosen_route = route
                for idx, p in enumerate(parts):
                    if rp[idx] and (rp[idx][0] == "<" and rp[idx][-1] == ">"):
                        (tp, varname) = rp[idx][1:-1].split(":")
                        tp = TYPE_MAP.get(tp)
                        if tp:
                            params[varname] = str(p)
                        else:
                            chosen_route = None
                            params = {}
                            break
                    elif p != rp[idx]:
                        chosen_route = None
                        params = {}
                        break
        return (self.routing.get(chosen_route), params)
