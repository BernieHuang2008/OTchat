class A:
    def __iter__(self):
        return iter({
            "a": 1,
            "b": 2
        })
    

print(dict(A()))