import os
import pickle
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

from pathlib import Path
from explain_core.interfaces.BaseInterface import BaseInterface


class NeoInterface(BaseInterface):
    def ans(self, state):
        if type(state) is bool:
            self.model.models["Ans"].is_enabled = state

    def pda(self, state):
        if type(state) is bool:
            self.model.models["Pda"].is_enabled = state

    def mob(self, state):
        if type(state) is bool:
            self.model.models["Mob"].is_enabled = state

    def metabolism(self, state):
        if type(state) is bool:
            self.model.models["Metabolism"].is_enabled = state

    def breathing(self, state):
        if type(state) is bool:
            self.model.models["Breathing"].switch_breathing(state)

    def ecls(self, state):
        if type(state) is bool:
            self.model.models["Ecls"].ecls_running = state

    def placenta(self, state):
        if type(state) is bool:
            self.model.models["Placenta"].switch_placenta(state)

    def ventilator(self, state):
        if type(state) is bool:
            self.model.models["Ventilator"].switch_ventilator(state)

    def resuscitation(self, state):
        if type(state) is bool:
            self.model.models["Resuscitation"].is_enabled = state

    def drugs(self, state):
        if type(state) is bool:
            self.model.models["Drugs"].is_enabled = state

    # plotters
    def plot_heart_pv_rt(self):
        self.plot_rt(
            ["LV.vol", "LV.pres"],
            autoscale=True,
            autoscale_interval=1.0,
            time_window=1.0,
            sample_interval=0.001,
            xy=True,
            update_interval=0.1,
        )

    def plot_vitals(self, time_to_calculate=30):
        self.plot_time_graph(
            ["AA.pres", "Heart.heart_rate", "Breathing.resp_rate", "AA.aboxy.so2"],
            time_to_calculate=time_to_calculate,
            combined=True,
            sharey=False,
            autoscale=True,
            ylowerlim=0,
            yupperlim=200,
            fill=False,
            fill_between=False,
        )

    def plot_bloodgas(self, time_to_calculate=30):
        self.plot_time_graph(
            ["AA.aboxy.ph", "AA.aboxy.pco2", "AA.aboxy.po2", "AA.aboxy.so2"],
            time_to_calculate=time_to_calculate,
            combined=False,
            sharey=False,
            fill=False,
        )

    def plot_ans(self, time_to_calculate=10):
        self.plot_time_graph(
            [
                "AA.aboxy.pco2",
                "Breathing.target_minute_volume",
                "Breathing.target_tidal_volume",
                "Breathing.resp_rate",
                "Breathing.exp_tidal_volume",
            ],
            time_to_calculate=time_to_calculate,
            combined=False,
            sharey=False,
            fill=False,
        )

    # lung plotters
    def plot_lung_pressures(
        self,
        time_to_calculate=10,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=False,
        analyze=False,
    ):
        self.plot_time_graph(
            ["DS.pres", "ALL.pres", "ALR.pres", "THORAX.pres"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_lung_volumes(
        self,
        time_to_calculate=10,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=False,
        analyze=False,
    ):
        self.plot_time_graph(
            ["ALL.vol", "ALR.vol"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_lung_flows(
        self,
        time_to_calculate=10,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=False,
        analyze=False,
    ):
        self.plot_time_graph(
            ["MOUTH_DS.flow", "DS_ALL.flow", "DS_ALR.flow"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_lung_pressures_left(
        self,
        time_to_calculate=10,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=False,
        analyze=False,
    ):
        self.plot_time_graph(
            ["DS.pres", "ALL.pres"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_lung_volumes_left(
        self,
        time_to_calculate=10,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=False,
        analyze=False,
    ):
        self.plot_time_graph(
            ["ALL.vol"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_ecls_po2(
        self,
        time_to_calculate=10,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=False,
        analyze=True,
    ):
        self.plot_time_graph(
            ["Ecls.pre_oxy_bg.po2", "Ecls.post_oxy_bg.po2", "Ecls.pat_bg.po2"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_ecls_pco2(
        self,
        time_to_calculate=10,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=False,
        analyze=True,
    ):
        self.plot_time_graph(
            ["Ecls.pre_oxy_bg.pco2", "Ecls.post_oxy_bg.pco2", "Ecls.pat_bg.pco2"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_ecls_flows(
        self,
        time_to_calculate=10,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=False,
        analyze=True,
    ):
        self.plot_time_graph(
            ["Ecls.blood_flow", "LV_AA.flow", "RV_PA.flow", "Pda.flow", "FO.flow"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_ecls_pressures(
        self,
        time_to_calculate=10,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=False,
        analyze=True,
    ):
        self.plot_time_graph(
            ["Ecls.p_ven", "Ecls.p_int", "Ecls.p_art", "RA.pres", "AD.pres"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_lung_flows_left(
        self,
        time_to_calculate=10,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=False,
        analyze=False,
    ):
        self.plot_time_graph(
            ["MOUTH_DS.flow", "DS_ALL.flow"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_lung_pressures_right(
        self,
        time_to_calculate=10,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=False,
        analyze=False,
    ):
        self.plot_time_graph(
            ["DS.pres", "ALR.pres"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_lung_volumes_right(
        self,
        time_to_calculate=10,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=False,
        analyze=False,
    ):
        self.plot_time_graph(
            ["ALR.vol"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_lung_flows_right(
        self,
        time_to_calculate=10,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=False,
        analyze=False,
    ):
        self.plot_time_graph(
            ["MOUTH_DS.flow", "DS_ALR.flow"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    # heart plotters
    def plot_heart_pressures(
        self,
        time_to_calculate=2,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=True,
        fill_between=False,
        analyze=False,
    ):
        self.plot_time_graph(
            ["LV.pres", "RV.pres", "LA.pres", "RA.pres", "AA.pres", "PA.pres"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_heart_volumes(
        self,
        time_to_calculate=2,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=True,
        analyze=False,
    ):
        self.plot_time_graph(
            ["LV.vol", "RV.vol", "LA.vol", "RA.vol"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_heart_flows(
        self,
        time_to_calculate=2,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=True,
        analyze=False,
    ):
        self.plot_time_graph(
            ["LA_LV.flow", "LV_AA.flow", "RA_RV.flow", "RV_PA.flow"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_heart_pressures_left(
        self,
        time_to_calculate=2,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=True,
        analyze=False,
    ):
        self.plot_time_graph(
            ["LV.pres", "LA.pres", "AA.pres"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_heart_flows_left(
        self,
        time_to_calculate=2,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=True,
        analyze=False,
    ):
        self.plot_time_graph(
            ["LA_LV.flow", "LV_AA.flow"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_heart_volumes_left(
        self,
        time_to_calculate=2,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=True,
        analyze=False,
    ):
        self.plot_time_graph(
            ["LA.vol", "LV.vol"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_heart_flows_right(
        self,
        time_to_calculate=2,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=True,
        analyze=False,
    ):
        self.plot_time_graph(
            ["RA_RV.flow", "RV_PA.flow"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_heart_volumes_right(
        self,
        time_to_calculate=2,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=True,
        analyze=False,
    ):
        self.plot_time_graph(
            ["RA.vol", "RV.vol"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_heart_pressures_right(
        self,
        time_to_calculate=2,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=True,
        analyze=False,
    ):
        self.plot_time_graph(
            ["RV.pres", "RA.pres", "PA.pres"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_heart_left(
        self,
        time_to_calculate=2,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=True,
        analyze=False,
    ):
        self.plot_time_graph(
            ["LA.pres", "LV.pres", "LA_LV.flow", "LV_AA.flow"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_heart_right(
        self,
        time_to_calculate=2,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=True,
        analyze=False,
    ):
        self.plot_time_graph(
            ["RA.pres", "RV.pres", "RA_RV.flow", "RV_PA.flow"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_da(
        self,
        time_to_calculate=2,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=True,
        analyze=False,
    ):
        self.plot_time_graph(
            ["DA.flow"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_ofo(
        self,
        time_to_calculate=2,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=True,
        analyze=False,
    ):
        self.plot_time_graph(
            ["FO.flow"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_shunts(
        self,
        time_to_calculate=2,
        combined=True,
        sharey=True,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=True,
        analyze=False,
    ):
        self.plot_time_graph(
            ["DA.flow", "FO.flow"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    def plot_ventilator_curves(
        self,
        time_to_calculate=5,
        combined=False,
        sharey=False,
        autoscale=True,
        ylowerlim=0,
        yupperlim=100,
        fill=False,
        analyze=False,
    ):
        self.plot_time_graph(
            ["Ventilator.pres", "Ventilator.flow", "Ventilator.vol", "Ventilator.co2"],
            time_to_calculate=time_to_calculate,
            autoscale=True,
            combined=combined,
            sharey=sharey,
            sampleinterval=0.0005,
            ylowerlim=ylowerlim,
            yupperlim=yupperlim,
            fill=fill,
            fill_between=False,
            analyze=analyze,
        )

    # getters
    def analyze_ecls(self, weight_based=True, time_to_calculate=60):
        self.analyze(
            [
                "Ecls.blood_flow",
                "Ecls.p_ven",
                "Ecls.p_int",
                "Ecls.p_art",
                "Ecls.tmp",
                "Ecls.pre_oxy_bg.ph",
                "Ecls.pre_oxy_bg.po2",
                "Ecls.pre_oxy_bg.pco2",
                "Ecls.pre_oxy_bg.hco3",
                "Ecls.pre_oxy_bg.be",
                "Ecls.pre_oxy_bg.so2",
                "Ecls.post_oxy_bg.ph",
                "Ecls.post_oxy_bg.po2",
                "Ecls.post_oxy_bg.pco2",
                "Ecls.post_oxy_bg.hco3",
                "Ecls.post_oxy_bg.be",
                "Ecls.post_oxy_bg.so2",
                "Ecls.pat_bg.ph",
                "Ecls.pat_bg.po2",
                "Ecls.pat_bg.pco2",
                "Ecls.pat_bg.hco3",
                "Ecls.pat_bg.be",
                "Ecls.pat_bg.so2",
            ],
            weight_based=weight_based,
            sampleinterval=0.0005,
            time_to_calculate=time_to_calculate,
        )

    def analyze_ventilator(self, weight_based=True, time_to_calculate=60):
        self.analyze(
            [
                "Ventilator.pres",
                "Ventilator.flow",
                "Ventilator.vent_rate",
                "Ventilator.etco2",
                "Ventilator.tv_kg",
            ],
            weight_based=weight_based,
            sampleinterval=0.0005,
            time_to_calculate=time_to_calculate,
        )

    def validate(self, weight_based=True, time_to_calculate=60):
        self.analyze(
            [
                "Heart.heart_rate",
                "AA.pres",
                "PA.pres",
                "LV_AA.flow",
                "RV_PA.flow",
                "SVC_RA.flow",
                "AAR_AD.flow",
                "COR_RA.flow",
                "DA_PA.flow",
                "FO.flow",
                "LV.vol",
                "RV.vol",
            ],
            weight_based=weight_based,
            sampleinterval=0.0005,
            time_to_calculate=time_to_calculate,
        )

    def validate_baseline(self, weight_based=True, time_to_calculate=60):
        result = self.analyze(
            [
                "Heart.heart_rate",
                "AA.pres",
                "PA.pres",
                "LV_AA.flow",
                "RV_PA.flow",
                "LV.vol",
                "RV.vol",
                "AAR_AD.flow",
                "SVC_RA.flow",
                "Pda.flow",
                "FO.flow",
            ],
            weight_based=weight_based,
            sampleinterval=0.0005,
            time_to_calculate=time_to_calculate,
            suppress_output=True,
        )

        vitals = self.get_vitals()

        # print the validation data
        print("")
        print(
            f" Model validation data for '{self.model.name}', weight: {self.model.weight} kg, gestational age: {self.model.gestational_age} wks"
        )
        print("")
        print(
            f" Heartrate      : {(result['Heart.heart_rate.max'] + result['Heart.heart_rate.min']) / 2.0:<0.0f} bpm"
        )
        print(
            f" Art pressure   : {result['AA.pres.max']:<0.0f}/{result['AA.pres.min']:<0.0f} ({result['AA.pres.mean']:<0.0f}) mmHg"
        )
        print(
            f" Pulm pressure  : {result['PA.pres.max']:<0.0f}/{result['PA.pres.min']:<0.0f} ({result['PA.pres.mean']:<0.0f}) mmHg"
        )
        print(f" LVO            : {result['LV_AA.flow.net']:<0.1f} ml/kg/min")
        print(f" LVEDV          : {result['LV.vol.max']:<0.1f} ml/kg")
        print(f" LVESV          : {result['LV.vol.min']:<0.1f} ml/kg")
        print(f" LVSV           : {result['LV_AA.flow.sv']:<0.1f} ml/kg")
        print(f" RVO            : {result['RV_PA.flow.net']:<0.1f} ml/kg/min")
        print(f" RVEDV          : {result['RV.vol.max']:<0.1f} ml/kg")
        print(f" RVESV          : {result['RV.vol.min']:<0.1f} ml/kg")
        print(f" RVSV           : {result['RV_PA.flow.sv']:<0.1f} ml/kg")
        print(
            f" LVO/RVO        : {round(result['LV_AA.flow.net']/result['RV_PA.flow.net'], 2)}"
        )
        print(f" DAo flow       : {result['AAR_AD.flow.net']:<0.1f} ml/kg/min")
        print(f" SVC flow       : {result['SVC_RA.flow.net']:<0.1f} ml/kg/min")
        print(
            f" PDA flow net   : {result['Pda.flow.net']:<0.1f} ml/kg/min, LtR: {result['Pda.flow.forward']:<0.1f} ml/kg/min, RtL: {-result['Pda.flow.backward']:<0.1f} ml/kg/min"
        )
        print(
            f" FO flow net    : {result['FO.flow.net']:<0.1f} ml/kg/min, LtR: {result['FO.flow.forward']:<0.1f} ml/kg/min, RtL: {-result['FO.flow.backward']:<0.1f} ml/kg/min"
        )
        print(f" Resp rate      : {vitals['resp_rate']:<0.0f} bpm")
        print(f" SpO2 pre       : {vitals['spo2_pre']:<0.0f} %")
        print(f" SpO2 post      : {vitals['spo2_post']:<0.0f} %")
        print(f" SpO2 ven       : {vitals['spo2_ven']:<0.0f} %")
        print(f" pH             : {vitals['pH']:<0.2f}")
        print(f" pCO2           : {vitals['pco2']:<0.1f} kPa")
        print(f" pO2            : {vitals['po2']:<0.1f} kPa")
        print(f" HCO3           : {vitals['hco3']:<0.1f} mmol/l")
        print(f" BE             : {vitals['be']:<0.1f} mmol/l")
        print("")

        return result

    def validate_pda(self, weight_based=True, time_to_calculate=60):
        result = self.analyze(
            [
                "Heart.heart_rate",
                "AA.pres",
                "LV_AA.flow",
                "RV_PA.flow",
                "SVC_RA.flow",
                "Pda.flow",
                "FO.flow",
            ],
            weight_based=weight_based,
            sampleinterval=0.0005,
            time_to_calculate=time_to_calculate,
            suppress_output=True,
        )

        # print the validation data
        print("")
        print(" Model validation data:")
        print(" ----------------------")
        print(
            f" Heart rate max : {result['Heart.heart_rate.max']:<10.0f} bpm, min: {result['Heart.heart_rate.min']:<10.0f} bpm."
        )
        print(
            f" Bloodpressure  : {result['AA.pres.max']:<0.0f}/{result['AA.pres.min']:<0.0f} ({result['AA.pres.mean']:<0.0f}) mmHg"
        )
        print(f" LVO            : {result['LV_AA.flow.net']:<0.1f} ml/kg/min")
        print(f" RVO            : {result['RV_PA.flow.net']:<0.1f} ml/kg/min")
        print(f" SVC flow       : {result['SVC_RA.flow.net']:<0.1f} ml/kg/min")
        print(
            f" PDA flow net   : {result['Pda.flow.net']:<0.1f} ml/kg/min, LtR: {result['Pda.flow.forward']:<0.1f} ml/kg/min, RtL: {-result['Pda.flow.backward']:<0.1f} ml/kg/min"
        )
        print(
            f" FO flow net    : {result['FO.flow.net']:<0.1f} ml/kg/min, LtR: {result['FO.flow.forward']:<0.1f} ml/kg/min, RtL: {-result['FO.flow.backward']:<0.1f} ml/kg/min"
        )
        print(
            f" LVO/RVO ratio  : {round(result['LV_AA.flow.net']/result['RV_PA.flow.net'], 2)}"
        )
        print("")

        return result

    def open_ductus_arteriosus(
        self, new_diameter: float, in_time: float = 10.0, at_time: float = 0.0
    ):
        self.model.models["Pda"].open_ductus(
            new_diameter=new_diameter, in_time=in_time, at_time=at_time
        )

    def close_ductus_arteriosus(self, in_time: float = 10.0, at_time: float = 0.0):
        self.model.models["Pda"].close_ductus(in_time=in_time, at_time=at_time)

    def analyze_heart(self, weight_based=True, time_to_calculate=60):
        self.analyze(
            [
                "AA.pres",
                "AD.pres",
                "PA.pres",
                "LA_LV.flow",
                "RA_RV.flow",
                "RV_PA.flow",
                "LV_AA.flow",
                "COR_RA.flow",
                "IVCI_RA.flow",
                "SVC_RA.flow",
                "Pda.flow",
                "FO.flow",
                "VSD.flow",
                "IPS.flow",
                "LA.pres_in",
                "RA.pres_in",
                "LV.pres_in",
                "RV.pres_in",
                "IVCI.pres",
                "LA.vol",
                "RA.vol",
                "LV.vol",
                "RV.vol",
                "Heart.heart_rate",
            ],
            weight_based=weight_based,
            sampleinterval=0.0005,
            time_to_calculate=time_to_calculate,
        )

    def get_vitals(self, time_to_calculate=10):
        self.get_bloodgas("AA")
        self.get_bloodgas("AD")
        self.get_bloodgas("RA")
        result = self.analyze(["AA.pres", "PA.pres", "IVCI.pres"], suppress_output=True)

        vitals = {
            "heartrate": self.model.models["Heart"].heart_rate,
            "spo2_pre": self.model.models["AA"].aboxy["so2"],
            "spo2_post": self.model.models["AD"].aboxy["so2"],
            "spo2_ven": self.model.models["RA"].aboxy["so2"],
            "abp_systole": result["AA.pres.max"],
            "abp_diastole": result["AA.pres.min"],
            "abp_mean": result["AA.pres.mean"],
            "pap_systole": result["PA.pres.max"],
            "pap_diastole": result["PA.pres.min"],
            "pap_mean": result["PA.pres.mean"],
            "cvp": result["IVCI.pres.min"]
            + 0.3333 * (result["IVCI.pres.max"] - result["IVCI.pres.min"]),
            "resp_rate": self.model.models["Breathing"].resp_rate,
            "pH": self.model.models["AD"].aboxy["ph"],
            "po2": self.model.models["AD"].aboxy["po2"] * 0.1333,
            "pco2": self.model.models["AD"].aboxy["pco2"] * 0.1333,
            "hco3": self.model.models["AD"].aboxy["hco3"],
            "be": self.model.models["AD"].aboxy["be"],
        }

        return vitals

    def get_gas_flows(self, time_to_calculate=10):
        self.model._datacollector.clear_watchlist()

        properties = []
        for component in self.model.models:
            component_type = self.model.models[component].model_type

            if component_type == "GasResistor":
                properties.append(component + ".flow")

        self.analyze(properties, time_to_calculate)

    def get_blood_flows(self, time_to_calculate=10):
        self.model._datacollector.clear_watchlist()

        properties = []
        for component in self.model.models:
            component_type = self.model.models[component].model_type

            if component_type == "Resistor":
                properties.append(component + ".flow")

        self.analyze(properties, time_to_calculate, sampleinterval=0.0005)

    def get_bloodgas(self, component="AA"):
        bc = self.model.models[component]
        result = self.model.models["Blood"].set_blood_composition(bc)
        if result:
            return {
                "ph": bc.aboxy["ph"],
                "po2": bc.aboxy["po2"] * 0.1333,
                "pco2": bc.aboxy["pco2"] * 0.1333,
                "hco3": bc.aboxy["hco3"],
                "be": bc.aboxy["be"],
                "so2": bc.aboxy["so2"],
            }

    def get_blood_pressures(self, time_to_calculate=10):
        self.model._datacollector.clear_watchlist()

        properties = []
        for component in self.model.models:
            component_type = self.model.models[component].model_type
            if (
                component_type == "BloodCapacitance"
                or component_type == "BloodTimeVaryingElastance"
            ):
                properties.append(component + ".pres")

        self.analyze(properties, time_to_calculate)

    def get_total_blood_volume(self):
        total_volume = 0
        pulm_blood_volume = 0
        pulm_cap_volume = 0
        syst_blood_volume = 0
        heart_volume = 0
        cap_volume = 0
        ven_volume = 0
        art_volume = 0
        upper_body = 0
        lower_body = 0

        for component in self.model.models:
            component_type = self.model.models[component].model_type

            if (
                component_type == "BloodCapacitance"
                or component_type == "BloodTimeVaryingElastance"
            ):
                total_volume += self.model.models[component].vol
            if component == "PA" or component == "PV":
                pulm_blood_volume += self.model.models[component].vol
            if component == "LL" or component == "RL":
                pulm_blood_volume += self.model.models[component].vol
                pulm_cap_volume += self.model.models[component].vol

            # heart
            if (
                component == "RA"
                or component == "RV"
                or component == "LA"
                or component == "LV"
                or component == "COR"
            ):
                heart_volume += self.model.models[component].vol
            # capillaries
            if (
                component == "RLB"
                or component == "RUB"
                or component == "BR"
                or component == "INT"
                or component == "LS"
                or component == "KID"
            ):
                cap_volume += self.model.models[component].vol
            # venous
            if component == "IVCI" or component == "IVCE" or component == "SVC":
                ven_volume += self.model.models[component].vol
            if component == "AA" or component == "AAR" or component == "AD":
                art_volume += self.model.models[component].vol
            if component == "RUB" or component == "BR" or component == "SVC":
                upper_body += self.model.models[component].vol
            if (
                component == "RLB"
                or component == "AAR"
                or component == "AA"
                or component == "AD"
                or component == "IVCI"
                or component == "IVCE"
                or component == "INT"
                or component == "LS"
                or component == "KID"
            ):
                lower_body += self.model.models[component].vol

        syst_blood_volume = total_volume - pulm_blood_volume

        print(
            f" Total blood volume: {total_volume * 1000 / self.model.weight} ml/kg = {total_volume / total_volume * 100}%"
        )
        print(
            f" Systemic blood volume: {syst_blood_volume * 1000 / self.model.weight} ml/kg = {syst_blood_volume / total_volume * 100}%"
        )
        print(
            f" Pulmonary total blood volume: {pulm_blood_volume * 1000 / self.model.weight} ml/kg = {pulm_blood_volume / total_volume * 100}%"
        )
        print(
            f" Pulmonary capillary blood volume: {pulm_cap_volume * 1000 / self.model.weight} ml/kg = {pulm_cap_volume / pulm_blood_volume * 100}% of total pulmonary blood volume"
        )
        print(
            f" Heart blood volume: {heart_volume * 1000 / self.model.weight} ml/kg = {heart_volume / total_volume * 100}%"
        )
        print(
            f" Capillary blood volume: {cap_volume * 1000 / self.model.weight} ml/kg = {cap_volume / total_volume * 100}%"
        )
        print(
            f" Venous blood volume: {ven_volume * 1000 / self.model.weight} ml/kg = {ven_volume / total_volume * 100}%"
        )
        print(
            f" Arterial blood volume: {art_volume * 1000 / self.model.weight} ml/kg = {art_volume / total_volume * 100}%"
        )
        print(
            f" Upper body blood volume: {upper_body * 1000 / self.model.weight} ml/kg = {upper_body / total_volume * 100}%"
        )
        print(
            f" Lower body blood volume: {lower_body * 1000 / self.model.weight} ml/kg = {lower_body / total_volume * 100}%"
        )

        return total_volume

    def get_blood_volumes(self, time_to_calculate=10):
        self.model._datacollector.clear_watchlist()

        properties = []
        for component in self.model.models:
            component_type = self.model.models[component].model_type

            if (
                component_type == "BloodCapacitance"
                or component_type == "BloodTimeVaryingElastance"
            ):
                properties.append(component + ".vol")

        self.analyze(properties, time_to_calculate)

    def get_gas_pressures(self, time_to_calculate=10):
        self.model._datacollector.clear_watchlist()

        properties = []
        for component in self.model.models:
            component_type = self.model.models[component].model_type

            if (
                component_type == "GasCapacitance"
                or component_type == "GasTimeVaryingElastance"
            ):
                properties.append(component + ".pres")

        self.analyze(properties, time_to_calculate)

    def get_gas_volumes(self, time_to_calculate=10):
        self.model._datacollector.clear_watchlist()

        properties = []
        for component in self.model.models:
            component_type = self.model.models[component].model_type

            if (
                component_type == "GasCapacitance"
                or component_type == "GasTimeVaryingElastance"
            ):
                properties.append(component + ".vol")

        self.analyze(properties, time_to_calculate)
