"""
Ensemble Models for Stock Price Prediction
Includes: Voting and Stacking Regressors with Multiple Algorithms
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import VotingRegressor, StackingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

class EnsembleModels:
    """Ensemble models for enhanced stock price prediction"""
    
    def __init__(self, X_train, y_train, X_test, y_test):
        """
        Initialize ensemble models
        
        Args:
            X_train, X_test: Training and test features
            y_train, y_test: Training and test targets
        """
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.scaler = StandardScaler()
        self.models = {}
        self.ensemble_models = {}
        self.predictions = {}
        self.metrics = {}
        
        # Scale the data
        self.X_train_scaled = self.scaler.fit_transform(X_train)
        self.X_test_scaled = self.scaler.transform(X_test)
        
        # Initialize base models
        self._initialize_base_models()
        
    def _initialize_base_models(self):
        """Initialize all base models"""
        self.models = {
            'Linear Regression': LinearRegression(),
            'Ridge Regression': Ridge(alpha=1.0, random_state=42),
            'Lasso Regression': Lasso(alpha=0.1, random_state=42),
            'Elastic Net': ElasticNet(alpha=0.1, l1_ratio=0.5, random_state=42),
            'SVR (Linear)': SVR(kernel='linear', C=1.0),
            'SVR (RBF)': SVR(kernel='rbf', C=1.0, gamma='scale'),
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'K-Neighbors': KNeighborsRegressor(n_neighbors=5),
            'Neural Network': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
        }
    
    def train_base_models(self):
        """Train all base models"""
        print("🔄 Training Base Models...")
        
        for name, model in self.models.items():
            try:
                print(f"   Training {name}...")
                model.fit(self.X_train_scaled, self.y_train)
                
                # Make predictions
                train_pred = model.predict(self.X_train_scaled)
                test_pred = model.predict(self.X_test_scaled)
                
                # Store predictions
                self.predictions[name] = {
                    'train': train_pred,
                    'test': test_pred
                }
                
                # Calculate metrics
                self.metrics[name] = {
                    'RMSE': np.sqrt(mean_squared_error(self.y_test, test_pred)),
                    'R²': r2_score(self.y_test, test_pred),
                    'MAE': mean_absolute_error(self.y_test, test_pred),
                    'MAPE': np.mean(np.abs((self.y_test - test_pred) / self.y_test)) * 100
                }
                
                print(f"   ✅ {name} - RMSE: {self.metrics[name]['RMSE']:.4f}, R²: {self.metrics[name]['R²']:.4f}")
                
            except Exception as e:
                print(f"   ❌ Error training {name}: {e}")
                continue
        
        return self.metrics
    
    def create_voting_ensemble(self, voting_method='soft', weights=None):
        """
        Create voting ensemble regressor
        
        Args:
            voting_method (str): 'hard' or 'soft' voting
            weights (list): Optional weights for each model
        """
        print(f"🔄 Creating Voting Ensemble ({voting_method} voting)...")
        
        # Select best performing models (top 5)
        sorted_models = sorted(self.metrics.items(), key=lambda x: x[1]['RMSE'])
        best_models = sorted_models[:5]
        
        # Create estimators list
        estimators = []
        for name, _ in best_models:
            if name in self.models:
                estimators.append((name, self.models[name]))
        
        # Create voting regressor
        if weights is None:
            weights = [1] * len(estimators)
        
        voting_regressor = VotingRegressor(
            estimators=estimators,
            voting=voting_method,
            weights=weights
        )
        
        # Train voting ensemble
        voting_regressor.fit(self.X_train_scaled, self.y_train)
        
        # Make predictions
        train_pred = voting_regressor.predict(self.X_train_scaled)
        test_pred = voting_regressor.predict(self.X_test_scaled)
        
        # Store results
        self.ensemble_models['Voting Ensemble'] = voting_regressor
        self.predictions['Voting Ensemble'] = {
            'train': train_pred,
            'test': test_pred
        }
        
        # Calculate metrics
        self.metrics['Voting Ensemble'] = {
            'RMSE': np.sqrt(mean_squared_error(self.y_test, test_pred)),
            'R²': r2_score(self.y_test, test_pred),
            'MAE': mean_absolute_error(self.y_test, test_pred),
            'MAPE': np.mean(np.abs((self.y_test - test_pred) / self.y_test)) * 100
        }
        
        print(f"   ✅ Voting Ensemble - RMSE: {self.metrics['Voting Ensemble']['RMSE']:.4f}, R²: {self.metrics['Voting Ensemble']['R²']:.4f}")
        
        return voting_regressor
    
    def create_stacking_ensemble(self, cv_folds=5):
        """
        Create stacking ensemble regressor
        
        Args:
            cv_folds (int): Number of cross-validation folds
        """
        print("🔄 Creating Stacking Ensemble...")
        
        # Select best performing models (top 5)
        sorted_models = sorted(self.metrics.items(), key=lambda x: x[1]['RMSE'])
        best_models = sorted_models[:5]
        
        # Create estimators list
        estimators = []
        for name, _ in best_models:
            if name in self.models:
                estimators.append((name, self.models[name]))
        
        # Create meta-learner
        meta_learner = LinearRegression()
        
        # Create stacking regressor
        stacking_regressor = StackingRegressor(
            estimators=estimators,
            final_estimator=meta_learner,
            cv=TimeSeriesSplit(n_splits=cv_folds),
            n_jobs=-1
        )
        
        # Train stacking ensemble
        stacking_regressor.fit(self.X_train_scaled, self.y_train)
        
        # Make predictions
        train_pred = stacking_regressor.predict(self.X_train_scaled)
        test_pred = stacking_regressor.predict(self.X_test_scaled)
        
        # Store results
        self.ensemble_models['Stacking Ensemble'] = stacking_regressor
        self.predictions['Stacking Ensemble'] = {
            'train': train_pred,
            'test': test_pred
        }
        
        # Calculate metrics
        self.metrics['Stacking Ensemble'] = {
            'RMSE': np.sqrt(mean_squared_error(self.y_test, test_pred)),
            'R²': r2_score(self.y_test, test_pred),
            'MAE': mean_absolute_error(self.y_test, test_pred),
            'MAPE': np.mean(np.abs((self.y_test - test_pred) / self.y_test)) * 100
        }
        
        print(f"   ✅ Stacking Ensemble - RMSE: {self.metrics['Stacking Ensemble']['RMSE']:.4f}, R²: {self.metrics['Stacking Ensemble']['R²']:.4f}")
        
        return stacking_regressor
    
    def create_weighted_ensemble(self, method='performance_based'):
        """
        Create weighted ensemble based on model performance
        
        Args:
            method (str): 'performance_based', 'equal', or 'custom'
        """
        print("🔄 Creating Weighted Ensemble...")
        
        # Select models with valid metrics
        valid_models = {name: metrics for name, metrics in self.metrics.items() 
                       if name in self.models and 'RMSE' in metrics}
        
        if not valid_models:
            print("   ❌ No valid models found for weighted ensemble")
            return None
        
        # Calculate weights based on method
        if method == 'performance_based':
            # Inverse RMSE weighting
            rmse_values = [metrics['RMSE'] for metrics in valid_models.values()]
            weights = [1/rmse for rmse in rmse_values]
            weights = [w/sum(weights) for w in weights]  # Normalize
            
        elif method == 'equal':
            weights = [1/len(valid_models)] * len(valid_models)
            
        elif method == 'custom':
            # Custom weights based on model type
            weights = []
            for name in valid_models.keys():
                if 'Regression' in name:
                    weights.append(0.3)
                elif 'Forest' in name or 'Boosting' in name:
                    weights.append(0.25)
                elif 'SVR' in name:
                    weights.append(0.2)
                else:
                    weights.append(0.1)
            weights = [w/sum(weights) for w in weights]  # Normalize
        
        # Create weighted predictions
        weighted_train_pred = np.zeros(len(self.y_train))
        weighted_test_pred = np.zeros(len(self.y_test))
        
        for i, (name, weight) in enumerate(zip(valid_models.keys(), weights)):
            model = self.models[name]
            train_pred = model.predict(self.X_train_scaled)
            test_pred = model.predict(self.X_test_scaled)
            
            weighted_train_pred += weight * train_pred
            weighted_test_pred += weight * test_pred
        
        # Store results
        self.predictions['Weighted Ensemble'] = {
            'train': weighted_train_pred,
            'test': weighted_test_pred
        }
        
        # Calculate metrics
        self.metrics['Weighted Ensemble'] = {
            'RMSE': np.sqrt(mean_squared_error(self.y_test, weighted_test_pred)),
            'R²': r2_score(self.y_test, weighted_test_pred),
            'MAE': mean_absolute_error(self.y_test, weighted_test_pred),
            'MAPE': np.mean(np.abs((self.y_test - weighted_test_pred) / self.y_test)) * 100
        }
        
        print(f"   ✅ Weighted Ensemble - RMSE: {self.metrics['Weighted Ensemble']['RMSE']:.4f}, R²: {self.metrics['Weighted Ensemble']['R²']:.4f}")
        
        return weighted_test_pred
    
    def cross_validate_ensemble(self, model_name, cv_folds=5):
        """
        Perform cross-validation on ensemble model
        
        Args:
            model_name (str): Name of the ensemble model
            cv_folds (int): Number of cross-validation folds
        """
        if model_name not in self.ensemble_models:
            print(f"❌ Model {model_name} not found")
            return None
        
        print(f"🔄 Cross-validating {model_name}...")
        
        model = self.ensemble_models[model_name]
        
        # Perform time series cross-validation
        tscv = TimeSeriesSplit(n_splits=cv_folds)
        
        cv_scores = cross_val_score(
            model, 
            self.X_train_scaled, 
            self.y_train, 
            cv=tscv, 
            scoring='neg_mean_squared_error',
            n_jobs=-1
        )
        
        # Convert to RMSE
        cv_rmse = np.sqrt(-cv_scores)
        
        print(f"   Cross-validation RMSE: {cv_rmse.mean():.4f} (+/- {cv_rmse.std() * 2:.4f})")
        
        return cv_rmse
    
    def get_ensemble_summary(self):
        """Get summary of all ensemble models"""
        summary = pd.DataFrame(self.metrics).T
        
        # Sort by RMSE (ascending)
        summary = summary.sort_values('RMSE')
        
        return summary
    
    def plot_ensemble_comparison(self):
        """Plot comparison of all models"""
        import matplotlib.pyplot as plt
        
        # Get summary
        summary = self.get_ensemble_summary()
        
        # Create comparison plot
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Ensemble Models Comparison', fontsize=16)
        
        # RMSE comparison
        axes[0, 0].bar(range(len(summary)), summary['RMSE'])
        axes[0, 0].set_title('RMSE Comparison (Lower is Better)')
        axes[0, 0].set_ylabel('RMSE')
        axes[0, 0].set_xticks(range(len(summary)))
        axes[0, 0].set_xticklabels(summary.index, rotation=45, ha='right')
        
        # R² comparison
        axes[0, 1].bar(range(len(summary)), summary['R²'])
        axes[0, 1].set_title('R² Comparison (Higher is Better)')
        axes[0, 1].set_ylabel('R²')
        axes[0, 1].set_xticks(range(len(summary)))
        axes[0, 1].set_xticklabels(summary.index, rotation=45, ha='right')
        
        # MAPE comparison
        axes[1, 0].bar(range(len(summary)), summary['MAPE'])
        axes[1, 0].set_title('MAPE Comparison (Lower is Better)')
        axes[1, 0].set_ylabel('MAPE (%)')
        axes[1, 0].set_xticks(range(len(summary)))
        axes[1, 0].set_xticklabels(summary.index, rotation=45, ha='right')
        
        # Predictions vs Actual
        best_model = summary.index[0]  # Best model (lowest RMSE)
        if best_model in self.predictions:
            test_pred = self.predictions[best_model]['test']
            axes[1, 1].scatter(self.y_test, test_pred, alpha=0.6)
            axes[1, 1].plot([self.y_test.min(), self.y_test.max()], 
                           [self.y_test.min(), self.y_test.max()], 'r--', lw=2)
            axes[1, 1].set_title(f'Predictions vs Actual ({best_model})')
            axes[1, 1].set_xlabel('Actual Values')
            axes[1, 1].set_ylabel('Predicted Values')
        
        plt.tight_layout()
        return fig
    
    def get_feature_importance(self, model_name):
        """Get feature importance for tree-based models"""
        if model_name not in self.ensemble_models:
            print(f"❌ Model {model_name} not found")
            return None
        
        model = self.ensemble_models[model_name]
        
        # Check if model has feature_importances_ attribute
        if hasattr(model, 'feature_importances_'):
            return model.feature_importances_
        elif hasattr(model, 'estimators_'):
            # For ensemble models, get average feature importance
            importances = []
            for estimator in model.estimators_:
                if hasattr(estimator, 'feature_importances_'):
                    importances.append(estimator.feature_importances_)
            
            if importances:
                return np.mean(importances, axis=0)
        
        print(f"❌ Feature importance not available for {model_name}")
        return None
    
    def predict_future(self, X_future, model_name=None):
        """
        Make future predictions using ensemble model
        
        Args:
            X_future: Future features
            model_name: Specific model to use (None for best model)
        """
        if model_name is None:
            # Use best performing model
            summary = self.get_ensemble_summary()
            model_name = summary.index[0]
        
        if model_name in self.ensemble_models:
            model = self.ensemble_models[model_name]
        elif model_name in self.models:
            model = self.models[model_name]
        else:
            print(f"❌ Model {model_name} not found")
            return None
        
        # Scale features
        X_future_scaled = self.scaler.transform(X_future)
        
        # Make predictions
        predictions = model.predict(X_future_scaled)
        
        return predictions
