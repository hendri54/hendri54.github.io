# Example to demonstrate Infiltrator

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