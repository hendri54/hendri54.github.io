var documenterSearchIndex = {"docs":
[{"location":"index.html#ModelObjectsLH-1","page":"ModelObjectsLH","title":"ModelObjectsLH","text":"","category":"section"},{"location":"index.html#","page":"ModelObjectsLH","title":"ModelObjectsLH","text":"This package defines the abstract ModelObject type and the ObjectId concept. ","category":"page"},{"location":"index.html#","page":"ModelObjectsLH","title":"ModelObjectsLH","text":"The idea is to provide a way of keeping track of where an object is located inside a model that consists of nested ModelObjects. This is useful for finding objects by ObjectId and for keeping track of where model parameters \"belong.\"","category":"page"},{"location":"index.html#ModelObject-1","page":"ModelObjectsLH","title":"ModelObject","text":"","category":"section"},{"location":"index.html#","page":"ModelObjectsLH","title":"ModelObjectsLH","text":"The abstract type ModelObject determines which objects the methods of ModelParams work on. Objects that are not subtypes of ModelObject are ignored.","category":"page"},{"location":"index.html#","page":"ModelObjectsLH","title":"ModelObjectsLH","text":"A ModelObject typically contains other ModelObjects. Each contains (potentially) calibrated parameters.","category":"page"},{"location":"index.html#","page":"ModelObjectsLH","title":"ModelObjectsLH","text":"ModelObject","category":"page"},{"location":"index.html#ModelObjectsLH.ModelObject","page":"ModelObjectsLH","title":"ModelObjectsLH.ModelObject","text":"ModelObject\n\nAbstract model object Must have field objId :: ObjectId that uniquely identifies it May contain a ParamVector, but need not.\n\nChild objects may be vectors. Then the vector must have a fixed element type that is a subtype of ModelObject\n\n\n\n\n\n","category":"type"},{"location":"index.html#[ObjectId](@ref)-1","page":"ModelObjectsLH","title":"ObjectId","text":"","category":"section"},{"location":"index.html#","page":"ModelObjectsLH","title":"ModelObjectsLH","text":"Each ModelObject has a unique ObjectId. It identifies where each object is located in the model hierarchy. Example: \":model > :firm > :technology\" would be (the string representation of) and ObjectId.","category":"page"},{"location":"index.html#","page":"ModelObjectsLH","title":"ModelObjectsLH","text":"The ObjectId keeps track of the parent object and of an index. The index is used when a vector of objects is created. For example, if we have several household types, their ObjectIds might be :hh[1], :hh[2], etc. ","category":"page"},{"location":"index.html#","page":"ModelObjectsLH","title":"ModelObjectsLH","text":"ObjectIds are automatically unique. Even if and object named :Foo occurs in different child objects of a ModelObject, the ObjectIds will be unique.","category":"page"},{"location":"index.html#","page":"ModelObjectsLH","title":"ModelObjectsLH","text":"Using an ObjectId, the corresponding object can be located inside the parent object without ambiguity.","category":"page"},{"location":"index.html#","page":"ModelObjectsLH","title":"ModelObjectsLH","text":"make_string produces a String representation of an ObjectId. This is useful for writing ObjectIds to text based data structures, such as JSON files. make_single_id does the reverse: it reconstructs the ObjectId from the string generated by make_string. This is used for reading ObjectId from text based files.","category":"page"},{"location":"index.html#","page":"ModelObjectsLH","title":"ModelObjectsLH","text":"ObjectIds can be constructed in several ways. make_object_id creates an ObjectId from its string representation.","category":"page"},{"location":"index.html#","page":"ModelObjectsLH","title":"ModelObjectsLH","text":"ObjectId\nget_object_id\nmake_string\nmake_child_id\nmake_single_id\nmake_object_id\nown_name","category":"page"},{"location":"index.html#ModelObjectsLH.ObjectId","page":"ModelObjectsLH","title":"ModelObjectsLH.ObjectId","text":"ObjectId\n\nComplete, unique ID of a ModelObject\n\nContains own id and a vector of parent ids, so one knows exactly where the object is placed in the model tree.\n\n\n\n\n\n","category":"type"},{"location":"index.html#ModelObjectsLH.make_string","page":"ModelObjectsLH","title":"ModelObjectsLH.make_string","text":"make_string(id)\n\n\nMake a string from a SingleId. Such as \"x[2, 1]\".\n\n\n\n\n\nmake_string(id)\n\n\nMake string from ObjectId. Such as \"p > q > r[4, 2]\".\n\n\n\n\n\n","category":"function"},{"location":"index.html#ModelObjectsLH.make_child_id","page":"ModelObjectsLH","title":"ModelObjectsLH.make_child_id","text":"make_child_id(obj, name)\nmake_child_id(obj, name, index)\n\n\nMake child ObjectId from parent ObjectId.\n\n\n\n\n\n","category":"function"},{"location":"index.html#ModelObjectsLH.make_single_id","page":"ModelObjectsLH","title":"ModelObjectsLH.make_single_id","text":"make_single_id(s)\n\n\nThe inverse of make_string.\n\n\n\n\n\n","category":"function"},{"location":"index.html#ModelObjectsLH.make_object_id","page":"ModelObjectsLH","title":"ModelObjectsLH.make_object_id","text":"The inverse of make_string.\n\n\n\n\n\n","category":"function"},{"location":"index.html#ModelObjectsLH.own_name","page":"ModelObjectsLH","title":"ModelObjectsLH.own_name","text":"own_name(oId)\n\n\nReturn object's own name as Symbol.\n\n\n\n\n\n","category":"function"},{"location":"index.html#","page":"ModelObjectsLH","title":"ModelObjectsLH","text":"","category":"page"}]
}