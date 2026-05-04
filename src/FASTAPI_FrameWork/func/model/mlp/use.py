import torch
from src.RelationGraph.func.utils.calc_matrix import build_matrix

def mlp_calc_proba(mlp_model, device, x_fused, y, class_names):

    mlp_model.eval()
    with torch.no_grad():
        x_tensor = torch.tensor(x_fused, dtype=torch.float32).to(device)
        logits = mlp_model(x_tensor)
        proba = torch.softmax(logits, dim=1).cpu().numpy()

    return build_matrix(proba, y, class_names, "affinity_matrix.json")