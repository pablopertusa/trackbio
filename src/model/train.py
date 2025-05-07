from src.model.model import get_model
import tensorflow as tf
import numpy as np
import keras
import json

def train_model(X_train: np.ndarray, X_test: np.ndarray, y_train: np.ndarray, y_test: np.ndarray, 
                batch_size: int = 8, print_model_summary: bool = False, save_history: bool = False, 
                history_path: str = "./training_history.json", debug: bool = False) -> np.ndarray:
    """
    Entrena una U-Net y la devuelve como resultado
    """
    img_size = X_train.shape[1:3]
    num_classes = 2
    num_channels = 15 # Las variables son el número de channels (los canales normales serían 3, RGB)

    model = get_model(img_size, num_classes, num_channels)

    if print_model_summary:
        print("Esto es un resumen del modelo que se va a utilizar para ajustar los datos")
        model.summary()
    
    # Ya sé que es raro hacerlo así, pero no se pueden crear instancias de keras.metrics dentro de los callbacks de 
    # metrics en tensorflow (ojalá saber por qué)
    # Y tampoco funciona poniendo metrics=["auc", "precision", "recall"], tengo un error de dimensiones, parece como que la funcionalidad
    # de coger la dimensión con mayor probabilidad (para poder hacer los cálculos) solo está implementada en "accuracy"
    rec = keras.metrics.Recall()
    def recall(y_true, y_pred):
        y_pred = tf.argmax(y_pred, axis=-1)
        rec.reset_state()
        rec.update_state(y_true, y_pred)
        resul = rec.result()
        return resul
    auc = keras.metrics.AUC()
    def AUC(y_true, y_pred):
        y_pred = tf.argmax(y_pred, axis=-1)
        auc.reset_state()
        auc.update_state(y_true, y_pred)
        resul = auc.result()
        return resul
    prec = keras.metrics.Precision()
    def precision(y_true, y_pred):
        y_pred = tf.argmax(y_pred, axis=-1)
        prec.reset_state()
        prec.update_state(y_true, y_pred)
        resul = prec.result()
        return resul

    model.compile(
        optimizer=keras.optimizers.Adam(1e-5), loss="sparse_categorical_crossentropy",
        metrics=["accuracy", recall, AUC, precision]
    )

    callbacks = [
        keras.callbacks.EarlyStopping(monitor="val_loss", patience=50, restore_best_weights=True),
        keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=10, min_lr=1e-8)
    ]

    if debug:
        epochs = 1
    else:
        epochs = 300

    # Train the model, doing validation at the end of each epoch.
    history = model.fit(
        X_train,
        y_train,
        epochs=epochs,
        validation_data=(X_test, y_test),
        callbacks=callbacks,
        batch_size=batch_size,
        verbose=2,
    )
    if save_history:
        with open(history_path, "w") as file:
            json.dump(history.history, file, indent=4)

    return model

def predict_model(X_test: np.ndarray, model: keras.Model) -> np.ndarray:
    y_pred = model.predict(X_test)
    y_pred_classes = np.argmax(y_pred, axis=-1)
    return y_pred_classes