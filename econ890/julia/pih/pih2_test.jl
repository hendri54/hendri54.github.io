## ----------  Testing PIH2
module PIH2Test

using Test

include("pih2.jl");
using .PIH2

# Again, in a function, so there are no side-effects.
function pih2_test(u :: AbstractUtility)
    m = Model(10.0, 1.05, 9, 0.98, u)
    ctV = pih2(m);

    @testset "PIH 2" begin
        @test all(ctV .> 0.0)
        @test ctV isa Vector{Float64}
        @test length(ctV) == m.T

        # Euler equation
        eeDevV = euler_dev(m, ctV);
        @test all(abs.(eeDevV .< 1e-6))

        # Budget constraint
        pvC = present_value(ctV, m.R);
        @test abs(pvC - m.Y) < 1e-6

        pvC2 = pv_cons(m, ctV[m.T]);
        @test isapprox(pvC2, m.Y, atol = 1e-6)
    end
end

# Testing solution by interpolation and root finding
function pih2_interp_test(u :: AbstractUtility)
    m = Model(10.0, 1.05, 9, 0.98, u)

    @testset "PIH 2 interpolation" begin
        ctV = solve_by_interpolation(m);
        ct2V = solve_by_root_finding(m);
        @test isapprox(ctV, ct2V, rtol = 1e-5)

        # Budget constraint
        pvC = present_value(ctV, m.R);
        @test abs(pvC - m.Y) < 1e-6      

        # Euler equation
        eeDevV = euler_dev(m, ctV);
        @test all(abs.(eeDevV .< 1e-6))
    end
end

@testset "PIH 2" begin
    for u ∈ (UtilityLog(), UtilityCRRA(2.0))
        pih2_test(u);
        pih2_interp_test(u);
    end
end

end

# -----------