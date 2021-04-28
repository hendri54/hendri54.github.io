# Example to demonstrate Infiltrator

# const ExampleDir = "/Users/lutz/Documents/data/web/professional/docs/econ890/julia/examples";
# using Pkg
# Pkg.add("Infiltrator");

using Infiltrator

function infil_test()
    for j = 1 : 10
        if iseven(j)
            @infiltrate
        end
        @show j
    end
    return nothing
end

infil_test()