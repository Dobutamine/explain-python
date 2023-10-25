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

    def artificial_whomb(self, state):
        if type(state) is bool:
            self.model.models["ArtificialWhomb"].ecls_running = state

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

    def analyze_heart(self, weight_based=True, time_to_calculate=60):
        self.analyze(
            [
                "AA.pres_in",
                "PA.pres_in",
                "LA_LV.flow",
                "RA_RV.flow",
                "RV_PA.flow",
                "LV_AA.flow",
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
        result = self.analyze(
            ["AD.pres_in", "PA.pres_in", "IVCI.pres_in"], suppress_output=True
        )

        vitals = {
            "heartrate": self.model.models["Heart"].heart_rate,
            "spo2_pre": self.model.models["AA"].aboxy["so2"],
            "spo2_post": self.model.models["AD"].aboxy["so2"],
            "abp_systole": result["AD.pres_in.max"],
            "abp_diastole": result["AD.pres_in.min"],
            "pap_systole": result["PA.pres_in.max"],
            "pap_diastole": result["PA.pres_in.min"],
            "cvp": result["IVCI.pres_in.min"]
            + 0.3333 * (result["IVCI.pres_in.max"] - result["IVCI.pres_in.min"]),
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
            f"Total blood volume: {total_volume * 1000 / self.model.weight} ml/kg = {total_volume / total_volume * 100}%"
        )
        print(
            f"Systemic blood volume: {syst_blood_volume * 1000 / self.model.weight} ml/kg = {syst_blood_volume / total_volume * 100}%"
        )
        print(
            f"Pulmonary total blood volume: {pulm_blood_volume * 1000 / self.model.weight} ml/kg = {pulm_blood_volume / total_volume * 100}%"
        )
        print(
            f"Pulmonary capillary blood volume: {pulm_cap_volume * 1000 / self.model.weight} ml/kg = {pulm_cap_volume / pulm_blood_volume * 100}% of total pulmonary blood volume"
        )
        print(
            f"Heart blood volume: {heart_volume * 1000 / self.model.weight} ml/kg = {heart_volume / total_volume * 100}%"
        )
        print(
            f"Capillary blood volume: {cap_volume * 1000 / self.model.weight} ml/kg = {cap_volume / total_volume * 100}%"
        )
        print(
            f"Venous blood volume: {ven_volume * 1000 / self.model.weight} ml/kg = {ven_volume / total_volume * 100}%"
        )
        print(
            f"Arterial blood volume: {art_volume * 1000 / self.model.weight} ml/kg = {art_volume / total_volume * 100}%"
        )
        print(
            f"Upper body blood volume: {upper_body * 1000 / self.model.weight} ml/kg = {upper_body / total_volume * 100}%"
        )
        print(
            f"Lower body blood volume: {lower_body * 1000 / self.model.weight} ml/kg = {lower_body / total_volume * 100}%"
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
