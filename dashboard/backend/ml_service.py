from prophet import Prophet

class MLService:
    def __init__(self):
        """
        Service ML pour prédictions Prophet
        Mode : Entraînement à la demande (on-demand) par action
        """
        self.model_loaded = True
        print("✅ Service ML Prophet initialisé (mode on-demand)")
    
    def create_model(self):
        """Crée une nouvelle instance de Prophet"""
        return Prophet(
            daily_seasonality=False,
            yearly_seasonality=True,
            weekly_seasonality=True,
            changepoint_prior_scale=0.05
        )

# Instance globale
ml_service = MLService()