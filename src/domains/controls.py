"""
Modeling and controls calculations for Engineering Calculations Database.

This module provides engineering calculations for control systems including:
- First-order system response
- Second-order system response
- Settling time
- Percent overshoot
- Ziegler-Nichols PID tuning
- PID controller output
- Gain margin
- Phase margin
"""

from __future__ import annotations

import math
from typing import Any

from src.core.calculations import (
    Calculation,
    CalculationResult,
    Parameter,
    register,
)
from src.core.units import Quantity


@register
class FirstOrderResponse(Calculation):
    """
    Calculate first-order system response characteristics.

    Transfer Function: G(s) = K / (tau*s + 1)

    Where:
        K = system gain (dimensionless)
        tau = time constant (s)

    For a step input of magnitude A:
        - Rise time (10% to 90%): t_r = 2.2 * tau
        - Settling time (2%): t_s = 4 * tau
        - Settling time (5%): t_s = 3 * tau
        - Final value: y_final = K * A
    """

    name = "First Order Response"
    category = "Controls"
    description = (
        "Calculate first-order system response characteristics. "
        "G(s) = K / (tau*s + 1)"
    )
    references = [
        "Modern Control Engineering, Ogata",
        "Control Systems Engineering, Nise",
    ]

    input_params = [
        Parameter("gain", "dimensionless", "System gain K"),
        Parameter("time_constant", "s", "Time constant tau"),
        Parameter("step_input", "dimensionless", "Step input magnitude"),
    ]
    output_params = [
        Parameter("rise_time", "s", "Rise time (10% to 90%)"),
        Parameter("settling_time_2pct", "s", "Settling time (2% criterion)"),
        Parameter("settling_time_5pct", "s", "Settling time (5% criterion)"),
        Parameter("final_value", "dimensionless", "Final steady-state value"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate first-order system response characteristics.

        Args:
            gain: System gain K as Quantity (dimensionless).
            time_constant: Time constant tau as Quantity (s).
            step_input: Step input magnitude as Quantity.

        Returns:
            CalculationResult with rise time, settling times, and final value.
        """
        self.reset()

        gain: Quantity = kwargs["gain"]
        time_constant: Quantity = kwargs["time_constant"]
        step_input: Quantity = kwargs["step_input"]

        inputs = {
            "gain": gain,
            "time_constant": time_constant,
            "step_input": step_input,
        }

        # Calculate rise time: t_r = 2.2 * tau (10% to 90%)
        rise_time = Quantity(2.2, "dimensionless") * time_constant
        self.add_step(
            description="Calculate rise time (10% to 90%)",
            formula="t_r = 2.2 * tau",
            result=rise_time,
            substitution=f"t_r = 2.2 * {time_constant} = {rise_time}",
        )

        # Calculate settling time (2% criterion): t_s = 4 * tau
        settling_time_2pct = Quantity(4.0, "dimensionless") * time_constant
        self.add_step(
            description="Calculate settling time (2% criterion)",
            formula="t_s(2%) = 4 * tau",
            result=settling_time_2pct,
            substitution=f"t_s(2%) = 4 * {time_constant} = {settling_time_2pct}",
        )

        # Calculate settling time (5% criterion): t_s = 3 * tau
        settling_time_5pct = Quantity(3.0, "dimensionless") * time_constant
        self.add_step(
            description="Calculate settling time (5% criterion)",
            formula="t_s(5%) = 3 * tau",
            result=settling_time_5pct,
            substitution=f"t_s(5%) = 3 * {time_constant} = {settling_time_5pct}",
        )

        # Calculate final value: y_final = K * A
        final_value = gain * step_input
        self.add_step(
            description="Calculate final steady-state value",
            formula="y_final = K * A",
            result=final_value,
            substitution=f"y_final = {gain} * {step_input} = {final_value}",
        )

        outputs = {
            "rise_time": rise_time,
            "settling_time_2pct": settling_time_2pct,
            "settling_time_5pct": settling_time_5pct,
            "final_value": final_value,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class SecondOrderResponse(Calculation):
    """
    Calculate second-order system response characteristics.

    Transfer Function: G(s) = omega_n^2 / (s^2 + 2*zeta*omega_n*s + omega_n^2)

    Where:
        omega_n = natural frequency (rad/s)
        zeta = damping ratio (dimensionless)

    Response characteristics for underdamped systems (0 < zeta < 1):
        - Rise time: t_r = (pi - arccos(zeta)) / omega_d
        - Peak time: t_p = pi / omega_d
        - Settling time (2%): t_s = 4 / (zeta * omega_n)
        - Percent overshoot: %OS = 100 * exp(-pi*zeta / sqrt(1-zeta^2))
        - Damped frequency: omega_d = omega_n * sqrt(1 - zeta^2)
    """

    name = "Second Order Response"
    category = "Controls"
    description = (
        "Calculate second-order system response characteristics. "
        "G(s) = omega_n^2 / (s^2 + 2*zeta*omega_n*s + omega_n^2)"
    )
    references = [
        "Modern Control Engineering, Ogata",
        "Control Systems Engineering, Nise",
    ]

    input_params = [
        Parameter("natural_freq", "rad/s", "Natural frequency omega_n"),
        Parameter("damping_ratio", "dimensionless", "Damping ratio zeta"),
        Parameter("gain", "dimensionless", "System DC gain K"),
    ]
    output_params = [
        Parameter("rise_time", "s", "Rise time (0% to 100%)"),
        Parameter("peak_time", "s", "Peak time"),
        Parameter("settling_time", "s", "Settling time (2% criterion)"),
        Parameter("percent_overshoot", "percent", "Percent overshoot"),
        Parameter("damped_freq", "rad/s", "Damped natural frequency"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate second-order system response characteristics.

        Args:
            natural_freq: Natural frequency omega_n as Quantity (rad/s).
            damping_ratio: Damping ratio zeta as Quantity (dimensionless).
            gain: System DC gain K as Quantity (dimensionless).

        Returns:
            CalculationResult with response characteristics.
        """
        self.reset()

        natural_freq: Quantity = kwargs["natural_freq"]
        damping_ratio: Quantity = kwargs["damping_ratio"]
        gain: Quantity = kwargs["gain"]

        inputs = {
            "natural_freq": natural_freq,
            "damping_ratio": damping_ratio,
            "gain": gain,
        }

        omega_n = natural_freq.magnitude
        zeta = damping_ratio.magnitude

        # Validate damping ratio for underdamped analysis
        if zeta < 0:
            raise ValueError(f"Damping ratio must be non-negative, got {zeta}")

        if zeta >= 1:
            # Critically damped or overdamped - special handling
            self.add_step(
                description="System is critically damped or overdamped (zeta >= 1)",
                formula="zeta >= 1",
                result=f"zeta = {zeta}",
                substitution="No oscillatory response characteristics apply",
            )
            # For critically/overdamped systems, approximate values
            damped_freq_value = 0.0
            percent_overshoot_value = 0.0
            # Approximations for overdamped systems
            rise_time_value = (2.16 * zeta + 0.60) / omega_n
            peak_time_value = float('inf')  # No peak for overdamped
            settling_time_value = 4.0 / (zeta * omega_n)
        else:
            # Underdamped system (0 < zeta < 1)
            # Calculate damped frequency: omega_d = omega_n * sqrt(1 - zeta^2)
            damped_freq_value = omega_n * math.sqrt(1 - zeta ** 2)
            self.add_step(
                description="Calculate damped natural frequency",
                formula="omega_d = omega_n * sqrt(1 - zeta^2)",
                result=damped_freq_value,
                substitution=f"omega_d = {omega_n} * sqrt(1 - {zeta}^2) = {damped_freq_value:.4f} rad/s",
            )

            # Calculate rise time: t_r = (pi - arccos(zeta)) / omega_d
            rise_time_value = (math.pi - math.acos(zeta)) / damped_freq_value
            self.add_step(
                description="Calculate rise time (0% to 100%)",
                formula="t_r = (pi - arccos(zeta)) / omega_d",
                result=rise_time_value,
                substitution=f"t_r = (pi - arccos({zeta})) / {damped_freq_value:.4f} = {rise_time_value:.4f} s",
            )

            # Calculate peak time: t_p = pi / omega_d
            peak_time_value = math.pi / damped_freq_value
            self.add_step(
                description="Calculate peak time",
                formula="t_p = pi / omega_d",
                result=peak_time_value,
                substitution=f"t_p = pi / {damped_freq_value:.4f} = {peak_time_value:.4f} s",
            )

            # Calculate settling time (2% criterion): t_s = 4 / (zeta * omega_n)
            settling_time_value = 4.0 / (zeta * omega_n)
            self.add_step(
                description="Calculate settling time (2% criterion)",
                formula="t_s = 4 / (zeta * omega_n)",
                result=settling_time_value,
                substitution=f"t_s = 4 / ({zeta} * {omega_n}) = {settling_time_value:.4f} s",
            )

            # Calculate percent overshoot: %OS = 100 * exp(-pi*zeta / sqrt(1-zeta^2))
            percent_overshoot_value = 100.0 * math.exp(
                -math.pi * zeta / math.sqrt(1 - zeta ** 2)
            )
            self.add_step(
                description="Calculate percent overshoot",
                formula="%OS = 100 * exp(-pi*zeta / sqrt(1-zeta^2))",
                result=percent_overshoot_value,
                substitution=(
                    f"%OS = 100 * exp(-pi*{zeta} / sqrt(1-{zeta}^2)) "
                    f"= {percent_overshoot_value:.2f}%"
                ),
            )

        outputs = {
            "rise_time": Quantity(rise_time_value, "s"),
            "peak_time": Quantity(peak_time_value, "s") if peak_time_value != float('inf') else Quantity(0, "s"),
            "settling_time": Quantity(settling_time_value, "s"),
            "percent_overshoot": Quantity(percent_overshoot_value, "percent"),
            "damped_freq": Quantity(damped_freq_value, "rad/s"),
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class SettlingTime(Calculation):
    """
    Calculate settling time for a second-order system.

    Formula (2% criterion): t_s = 4 / (zeta * omega_n)
    Formula (5% criterion): t_s = 3 / (zeta * omega_n)

    Where:
        t_s = settling time (s)
        zeta = damping ratio (dimensionless)
        omega_n = natural frequency (rad/s)
    """

    name = "Settling Time"
    category = "Controls"
    description = (
        "Calculate settling time for a second-order system. "
        "t_s = 4/(zeta*omega_n) for 2%, t_s = 3/(zeta*omega_n) for 5%"
    )
    references = [
        "Modern Control Engineering, Ogata",
        "Control Systems Engineering, Nise",
    ]

    input_params = [
        Parameter("damping_ratio", "dimensionless", "Damping ratio zeta"),
        Parameter("natural_freq_rad", "rad/s", "Natural frequency omega_n"),
        Parameter("criterion", "dimensionless", "Settling criterion (2 or 5 percent)"),
    ]
    output_params = [
        Parameter("settling_time", "s", "Settling time"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate settling time.

        Args:
            damping_ratio: Damping ratio zeta as Quantity (dimensionless).
            natural_freq_rad: Natural frequency omega_n as Quantity (rad/s).
            criterion: Settling criterion (2 or 5) as Quantity (dimensionless).

        Returns:
            CalculationResult with settling time.
        """
        self.reset()

        damping_ratio: Quantity = kwargs["damping_ratio"]
        natural_freq_rad: Quantity = kwargs["natural_freq_rad"]
        criterion: Quantity = kwargs["criterion"]

        inputs = {
            "damping_ratio": damping_ratio,
            "natural_freq_rad": natural_freq_rad,
            "criterion": criterion,
        }

        zeta = damping_ratio.magnitude
        omega_n = natural_freq_rad.magnitude
        crit = criterion.magnitude

        # Validate damping ratio
        if zeta <= 0:
            raise ValueError(f"Damping ratio must be positive, got {zeta}")

        # Validate criterion
        if crit not in [2, 5]:
            raise ValueError(f"Criterion must be 2 or 5, got {crit}")

        # Select multiplier based on criterion
        if crit == 2:
            multiplier = 4.0
            formula = "t_s = 4 / (zeta * omega_n)"
        else:
            multiplier = 3.0
            formula = "t_s = 3 / (zeta * omega_n)"

        self.add_step(
            description=f"Using {int(crit)}% settling criterion",
            formula=formula,
            result=f"multiplier = {multiplier}",
            substitution=f"For {int(crit)}% criterion, use multiplier = {multiplier}",
        )

        # Calculate settling time: t_s = multiplier / (zeta * omega_n)
        settling_time_value = multiplier / (zeta * omega_n)
        self.add_step(
            description="Calculate settling time",
            formula=formula,
            result=settling_time_value,
            substitution=f"t_s = {multiplier} / ({zeta} * {omega_n}) = {settling_time_value:.4f} s",
        )

        outputs = {
            "settling_time": Quantity(settling_time_value, "s"),
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class PercentOvershoot(Calculation):
    """
    Calculate percent overshoot for a second-order underdamped system.

    Formula: %OS = 100 * exp(-pi*zeta / sqrt(1-zeta^2))

    Where:
        %OS = percent overshoot (%)
        zeta = damping ratio (dimensionless, 0 < zeta < 1)
    """

    name = "Percent Overshoot"
    category = "Controls"
    description = (
        "Calculate percent overshoot for second-order system. "
        "%OS = 100 * exp(-pi*zeta / sqrt(1-zeta^2))"
    )
    references = [
        "Modern Control Engineering, Ogata",
        "Control Systems Engineering, Nise",
    ]

    input_params = [
        Parameter("damping_ratio", "dimensionless", "Damping ratio zeta (0 < zeta < 1)"),
    ]
    output_params = [
        Parameter("percent_overshoot", "percent", "Percent overshoot"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate percent overshoot.

        Args:
            damping_ratio: Damping ratio zeta as Quantity (dimensionless).

        Returns:
            CalculationResult with percent overshoot.
        """
        self.reset()

        damping_ratio: Quantity = kwargs["damping_ratio"]

        inputs = {
            "damping_ratio": damping_ratio,
        }

        zeta = damping_ratio.magnitude

        # Validate damping ratio for underdamped system
        if zeta < 0 or zeta >= 1:
            raise ValueError(
                f"Damping ratio must be in range [0, 1) for underdamped system, got {zeta}"
            )

        # Calculate percent overshoot: %OS = 100 * exp(-pi*zeta / sqrt(1-zeta^2))
        if zeta == 0:
            # Undamped system has 100% overshoot
            percent_overshoot_value = 100.0
            self.add_step(
                description="Undamped system (zeta = 0) has maximum overshoot",
                formula="%OS = 100% for zeta = 0",
                result=percent_overshoot_value,
                substitution="%OS = 100%",
            )
        else:
            exponent = -math.pi * zeta / math.sqrt(1 - zeta ** 2)
            self.add_step(
                description="Calculate exponent term",
                formula="exponent = -pi*zeta / sqrt(1-zeta^2)",
                result=exponent,
                substitution=f"exponent = -pi*{zeta} / sqrt(1-{zeta}^2) = {exponent:.4f}",
            )

            percent_overshoot_value = 100.0 * math.exp(exponent)
            self.add_step(
                description="Calculate percent overshoot",
                formula="%OS = 100 * exp(exponent)",
                result=percent_overshoot_value,
                substitution=f"%OS = 100 * exp({exponent:.4f}) = {percent_overshoot_value:.2f}%",
            )

        outputs = {
            "percent_overshoot": Quantity(percent_overshoot_value, "percent"),
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class ZieglerNicholsTuning(Calculation):
    """
    Calculate PID controller gains using Ziegler-Nichols tuning method.

    Based on ultimate gain (Ku) and ultimate period (Tu):
        P controller:  Kp = 0.5*Ku
        PI controller: Kp = 0.45*Ku, Ki = Kp/(0.83*Tu)
        PID controller: Kp = 0.6*Ku, Ki = Kp/(0.5*Tu), Kd = Kp*0.125*Tu

    Where:
        Ku = ultimate gain (dimensionless) - gain at which system oscillates
        Tu = ultimate period (s) - period of sustained oscillation
    """

    name = "Ziegler-Nichols Tuning"
    category = "Controls"
    description = (
        "Calculate PID gains using Ziegler-Nichols ultimate gain method. "
        "Based on Ku (ultimate gain) and Tu (ultimate period)."
    )
    references = [
        "Ziegler, J.G. and Nichols, N.B. (1942)",
        "Process Control Instrumentation Technology, Johnson",
    ]

    input_params = [
        Parameter("ultimate_gain", "dimensionless", "Ultimate gain Ku"),
        Parameter("ultimate_period", "s", "Ultimate period Tu"),
        Parameter("controller_type", "dimensionless", "Controller type: 1=P, 2=PI, 3=PID"),
    ]
    output_params = [
        Parameter("kp", "dimensionless", "Proportional gain"),
        Parameter("ki", "1/s", "Integral gain"),
        Parameter("kd", "s", "Derivative gain"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate PID gains using Ziegler-Nichols tuning.

        Args:
            ultimate_gain: Ultimate gain Ku as Quantity (dimensionless).
            ultimate_period: Ultimate period Tu as Quantity (s).
            controller_type: Controller type (1=P, 2=PI, 3=PID) as Quantity.

        Returns:
            CalculationResult with PID gains.
        """
        self.reset()

        ultimate_gain: Quantity = kwargs["ultimate_gain"]
        ultimate_period: Quantity = kwargs["ultimate_period"]
        controller_type: Quantity = kwargs["controller_type"]

        inputs = {
            "ultimate_gain": ultimate_gain,
            "ultimate_period": ultimate_period,
            "controller_type": controller_type,
        }

        ku = ultimate_gain.magnitude
        tu = ultimate_period.magnitude
        ctrl_type = int(controller_type.magnitude)

        # Validate controller type
        if ctrl_type not in [1, 2, 3]:
            raise ValueError(
                f"Controller type must be 1 (P), 2 (PI), or 3 (PID), got {ctrl_type}"
            )

        type_names = {1: "P", 2: "PI", 3: "PID"}
        self.add_step(
            description=f"Ziegler-Nichols tuning for {type_names[ctrl_type]} controller",
            formula=f"Controller type: {type_names[ctrl_type]}",
            result=f"Ku = {ku}, Tu = {tu} s",
            substitution=f"Using ultimate gain method with Ku = {ku}, Tu = {tu} s",
        )

        if ctrl_type == 1:  # P controller
            kp_value = 0.5 * ku
            ki_value = 0.0
            kd_value = 0.0
            self.add_step(
                description="Calculate P controller gain",
                formula="Kp = 0.5 * Ku",
                result=kp_value,
                substitution=f"Kp = 0.5 * {ku} = {kp_value:.4f}",
            )
        elif ctrl_type == 2:  # PI controller
            kp_value = 0.45 * ku
            ti = 0.83 * tu  # Integral time
            ki_value = kp_value / ti
            kd_value = 0.0
            self.add_step(
                description="Calculate PI controller gains",
                formula="Kp = 0.45*Ku, Ti = 0.83*Tu, Ki = Kp/Ti",
                result=(kp_value, ki_value),
                substitution=(
                    f"Kp = 0.45*{ku} = {kp_value:.4f}, "
                    f"Ti = 0.83*{tu} = {ti:.4f} s, "
                    f"Ki = {kp_value:.4f}/{ti:.4f} = {ki_value:.4f} 1/s"
                ),
            )
        else:  # PID controller
            kp_value = 0.6 * ku
            ti = 0.5 * tu  # Integral time
            td = 0.125 * tu  # Derivative time
            ki_value = kp_value / ti
            kd_value = kp_value * td
            self.add_step(
                description="Calculate PID controller gains",
                formula="Kp = 0.6*Ku, Ti = 0.5*Tu, Td = 0.125*Tu, Ki = Kp/Ti, Kd = Kp*Td",
                result=(kp_value, ki_value, kd_value),
                substitution=(
                    f"Kp = 0.6*{ku} = {kp_value:.4f}, "
                    f"Ti = 0.5*{tu} = {ti:.4f} s, "
                    f"Td = 0.125*{tu} = {td:.4f} s, "
                    f"Ki = {kp_value:.4f}/{ti:.4f} = {ki_value:.4f} 1/s, "
                    f"Kd = {kp_value:.4f}*{td:.4f} = {kd_value:.4f} s"
                ),
            )

        outputs = {
            "kp": Quantity(kp_value, "dimensionless"),
            "ki": Quantity(ki_value, "1/s"),
            "kd": Quantity(kd_value, "s"),
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class PIDControllerOutput(Calculation):
    """
    Calculate PID controller output.

    Formula: u(t) = Kp*e + Ki*integral(e) + Kd*de/dt

    Where:
        u(t) = controller output
        Kp = proportional gain
        Ki = integral gain
        Kd = derivative gain
        e = error (setpoint - measured value)
        integral(e) = integral of error over time
        de/dt = derivative of error (rate of change)
    """

    name = "PID Controller Output"
    category = "Controls"
    description = (
        "Calculate PID controller output. "
        "u(t) = Kp*e + Ki*integral(e) + Kd*de/dt"
    )
    references = [
        "Process Control Instrumentation Technology, Johnson",
        "Feedback Control of Dynamic Systems, Franklin",
    ]

    input_params = [
        Parameter("kp", "dimensionless", "Proportional gain"),
        Parameter("ki", "1/s", "Integral gain"),
        Parameter("kd", "s", "Derivative gain"),
        Parameter("error", "dimensionless", "Current error"),
        Parameter("error_integral", "s", "Integral of error (error*time)"),
        Parameter("error_derivative", "1/s", "Derivative of error (de/dt)"),
    ]
    output_params = [
        Parameter("controller_output", "dimensionless", "Controller output u(t)"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate PID controller output.

        Args:
            kp: Proportional gain as Quantity (dimensionless).
            ki: Integral gain as Quantity (1/s).
            kd: Derivative gain as Quantity (s).
            error: Current error as Quantity (dimensionless).
            error_integral: Integral of error as Quantity (s).
            error_derivative: Derivative of error as Quantity (1/s).

        Returns:
            CalculationResult with controller output.
        """
        self.reset()

        kp: Quantity = kwargs["kp"]
        ki: Quantity = kwargs["ki"]
        kd: Quantity = kwargs["kd"]
        error: Quantity = kwargs["error"]
        error_integral: Quantity = kwargs["error_integral"]
        error_derivative: Quantity = kwargs["error_derivative"]

        inputs = {
            "kp": kp,
            "ki": ki,
            "kd": kd,
            "error": error,
            "error_integral": error_integral,
            "error_derivative": error_derivative,
        }

        # Calculate proportional term: P = Kp * e
        p_term = kp * error
        self.add_step(
            description="Calculate proportional term",
            formula="P = Kp * e",
            result=p_term,
            substitution=f"P = {kp} * {error} = {p_term}",
        )

        # Calculate integral term: I = Ki * integral(e)
        i_term = ki * error_integral
        self.add_step(
            description="Calculate integral term",
            formula="I = Ki * integral(e)",
            result=i_term,
            substitution=f"I = {ki} * {error_integral} = {i_term}",
        )

        # Calculate derivative term: D = Kd * de/dt
        d_term = kd * error_derivative
        self.add_step(
            description="Calculate derivative term",
            formula="D = Kd * de/dt",
            result=d_term,
            substitution=f"D = {kd} * {error_derivative} = {d_term}",
        )

        # Calculate total output: u(t) = P + I + D
        controller_output = p_term + i_term + d_term
        self.add_step(
            description="Calculate total PID output",
            formula="u(t) = P + I + D",
            result=controller_output,
            substitution=f"u(t) = {p_term} + {i_term} + {d_term} = {controller_output}",
        )

        outputs = {
            "controller_output": controller_output,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class GainMargin(Calculation):
    """
    Calculate gain margin from system frequency response.

    Formula: GM = 1 / |G(j*omega_pc)|

    Where:
        GM = gain margin (dimensionless)
        |G(j*omega_pc)| = magnitude at phase crossover frequency
                          (where phase = -180 degrees)

    The gain margin in dB:
        GM_dB = 20 * log10(GM) = -20 * log10(|G(j*omega_pc)|)
    """

    name = "Gain Margin"
    category = "Controls"
    description = (
        "Calculate gain margin from frequency response magnitude at phase crossover. "
        "GM = 1/|G(j*omega_pc)| where phase = -180 deg"
    )
    references = [
        "Modern Control Engineering, Ogata",
        "Feedback Control of Dynamic Systems, Franklin",
    ]

    input_params = [
        Parameter(
            "magnitude_at_phase_crossover",
            "dimensionless",
            "Magnitude |G(jw)| at phase crossover (phase = -180 deg)",
        ),
    ]
    output_params = [
        Parameter("gain_margin", "dimensionless", "Gain margin (linear)"),
        Parameter("gain_margin_db", "dB", "Gain margin in decibels"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate gain margin.

        Args:
            magnitude_at_phase_crossover: Magnitude at phase crossover as Quantity.

        Returns:
            CalculationResult with gain margin (linear and dB).
        """
        self.reset()

        magnitude_at_phase_crossover: Quantity = kwargs["magnitude_at_phase_crossover"]

        inputs = {
            "magnitude_at_phase_crossover": magnitude_at_phase_crossover,
        }

        mag = magnitude_at_phase_crossover.magnitude

        # Validate magnitude
        if mag <= 0:
            raise ValueError(f"Magnitude must be positive, got {mag}")

        # Calculate gain margin: GM = 1 / |G(j*omega_pc)|
        gain_margin_value = 1.0 / mag
        self.add_step(
            description="Calculate gain margin (linear)",
            formula="GM = 1 / |G(j*omega_pc)|",
            result=gain_margin_value,
            substitution=f"GM = 1 / {mag} = {gain_margin_value:.4f}",
        )

        # Calculate gain margin in dB: GM_dB = 20 * log10(GM)
        gain_margin_db_value = 20.0 * math.log10(gain_margin_value)
        self.add_step(
            description="Calculate gain margin in decibels",
            formula="GM_dB = 20 * log10(GM)",
            result=gain_margin_db_value,
            substitution=f"GM_dB = 20 * log10({gain_margin_value:.4f}) = {gain_margin_db_value:.2f} dB",
        )

        # Stability assessment
        if gain_margin_value > 1:
            stability = "System is stable (GM > 1, GM_dB > 0)"
        elif gain_margin_value == 1:
            stability = "System is marginally stable (GM = 1, GM_dB = 0)"
        else:
            stability = "System is unstable (GM < 1, GM_dB < 0)"

        self.add_step(
            description="Assess stability based on gain margin",
            formula="GM > 1 (or GM_dB > 0) indicates stability",
            result=stability,
            substitution=f"GM = {gain_margin_value:.4f} -> {stability}",
        )

        outputs = {
            "gain_margin": Quantity(gain_margin_value, "dimensionless"),
            "gain_margin_db": Quantity(gain_margin_db_value, "dB"),
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class PhaseMargin(Calculation):
    """
    Calculate phase margin from system frequency response.

    Formula: PM = 180 + phase(G(j*omega_gc))

    Where:
        PM = phase margin (degrees)
        phase(G(j*omega_gc)) = phase angle at gain crossover frequency
                               (where |G| = 1)

    Note: phase(G(j*omega_gc)) is typically negative for stable systems.
    """

    name = "Phase Margin"
    category = "Controls"
    description = (
        "Calculate phase margin from frequency response phase at gain crossover. "
        "PM = 180 + phase(G(j*omega_gc)) where |G| = 1"
    )
    references = [
        "Modern Control Engineering, Ogata",
        "Feedback Control of Dynamic Systems, Franklin",
    ]

    input_params = [
        Parameter(
            "phase_at_gain_crossover",
            "deg",
            "Phase angle at gain crossover (where |G| = 1)",
        ),
    ]
    output_params = [
        Parameter("phase_margin", "deg", "Phase margin"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate phase margin.

        Args:
            phase_at_gain_crossover: Phase at gain crossover as Quantity (degrees).

        Returns:
            CalculationResult with phase margin.
        """
        self.reset()

        phase_at_gain_crossover: Quantity = kwargs["phase_at_gain_crossover"]

        inputs = {
            "phase_at_gain_crossover": phase_at_gain_crossover,
        }

        phase = phase_at_gain_crossover.magnitude

        # Calculate phase margin: PM = 180 + phase(G)
        # Note: phase is typically negative (e.g., -150 deg)
        phase_margin_value = 180.0 + phase
        self.add_step(
            description="Calculate phase margin",
            formula="PM = 180 + phase(G(j*omega_gc))",
            result=phase_margin_value,
            substitution=f"PM = 180 + ({phase}) = {phase_margin_value:.2f} deg",
        )

        # Stability assessment
        if phase_margin_value > 0:
            stability = "System is stable (PM > 0)"
        elif phase_margin_value == 0:
            stability = "System is marginally stable (PM = 0)"
        else:
            stability = "System is unstable (PM < 0)"

        self.add_step(
            description="Assess stability based on phase margin",
            formula="PM > 0 indicates stability",
            result=stability,
            substitution=f"PM = {phase_margin_value:.2f} deg -> {stability}",
        )

        outputs = {
            "phase_margin": Quantity(phase_margin_value, "deg"),
        }

        return self.format_result(inputs=inputs, outputs=outputs)


# Module exports
__all__ = [
    "FirstOrderResponse",
    "SecondOrderResponse",
    "SettlingTime",
    "PercentOvershoot",
    "ZieglerNicholsTuning",
    "PIDControllerOutput",
    "GainMargin",
    "PhaseMargin",
]
