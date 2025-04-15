from src.model.model import get_model
import numpy as np
import keras

def train_model(X_train: np.ndarray, X_test: np.ndarray, y_train: np.ndarray, y_test: np.ndarray, 
                batch_size: int = 8, print_model_summary: bool = False) -> np.ndarray:
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

    model.compile(
        optimizer=keras.optimizers.Adam(1e-4), loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    callbacks = [
        keras.callbacks.EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
        keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.1, patience=3)
    ]

    # Train the model, doing validation at the end of each epoch.
    epochs = 200
    history = model.fit(
        X_train,
        y_train,
        epochs=epochs,
        validation_data=(X_test, y_test),
        callbacks=callbacks,
        batch_size=batch_size,
        verbose=2,
    )

    return model, history

def predict_model(X_test: np.ndarray, model: keras.Model) -> np.ndarray:
    y_pred = model.predict(X_test)
    y_pred_classes = np.argmax(y_pred, axis=-1)
    return y_pred_classes