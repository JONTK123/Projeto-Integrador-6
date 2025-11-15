"""
Seletor automático de melhor modelo do MLflow
Compara todos os modelos treinados e identifica o melhor baseado em métricas
"""

from typing import Optional, Dict, Tuple
import mlflow
from mlflow.tracking import MlflowClient
from app.core.mlflow_config import (
    get_client,
    EXPERIMENT_NAME,
    MODEL_NAME,
    get_production_model_version
)


def find_best_model_by_metrics(metric_name: str = "test_precision_at_10") -> Optional[Tuple[str, Dict]]:
    """
    Encontra o melhor modelo baseado em métricas, ignorando modelos com warnings
    
    Args:
        metric_name: Nome da métrica para comparar (padrão: test_precision_at_10)
    
    Returns:
        Tupla (run_id, info_dict) do melhor modelo ou None
    """
    try:
        client = get_client()
        if client is None:
            return None
        
        experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
        if experiment is None:
            return None
        
        # Buscar todos os runs
        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            max_results=1000
        )
        
        if not runs:
            return None
        
        # Filtrar e avaliar runs válidos
        valid_models = []
        models_with_warnings = []
        
        for run in runs:
            metrics = run.data.metrics
            
            # Verificar se tem warning
            has_warning = "evaluation_warning" in metrics
            
            # Obter métrica principal
            main_metric = metrics.get(metric_name)
            if main_metric is None:
                continue
            
            # Converter para float
            try:
                if hasattr(main_metric, 'value'):
                    metric_value = float(main_metric.value)
                else:
                    metric_value = float(main_metric)
            except (ValueError, TypeError):
                continue
            
            # Coletar outras métricas importantes
            other_metrics = {}
            for key in ["test_auc", "test_recall_at_10", "test_f1_at_10", "test_mrr"]:
                if key in metrics:
                    val = metrics[key]
                    try:
                        if hasattr(val, 'value'):
                            other_metrics[key] = float(val.value)
                        else:
                            other_metrics[key] = float(val)
                    except:
                        pass
            
            model_info = {
                "run_id": run.info.run_id,
                "metric_value": metric_value,
                "metrics": metrics,
                "params": run.data.params,
                "other_metrics": other_metrics,
                "has_warning": has_warning
            }
            
            # Separar modelos com e sem warnings
            if has_warning:
                models_with_warnings.append(model_info)
            else:
                valid_models.append(model_info)
        
        # Se não houver modelos sem warnings, usar modelos com warnings como fallback
        if not valid_models and models_with_warnings:
            print("⚠️  Nenhum modelo sem warnings encontrado. Usando melhor modelo com warnings como fallback.")
            valid_models = models_with_warnings
        
        if not valid_models:
            return None
        
        # Ordenar por métrica principal (descendente)
        valid_models.sort(key=lambda x: x["metric_value"], reverse=True)
        best = valid_models[0]
        
        return (best["run_id"], {
            "run_id": best["run_id"],
            "metric_value": best["metric_value"],
            "metric_name": metric_name,
            "metrics": best["metrics"],
            "params": best["params"],
            "other_metrics": best["other_metrics"]
        })
        
    except Exception as e:
        print(f"⚠️  Erro ao buscar melhor modelo: {e}")
        return None


def evaluate_and_register_if_best(new_run_id: str, metric_name: str = "test_precision_at_10", metric_value: float = 0.0) -> bool:
    """
    Avalia se o NOVO modelo é melhor que o atual e registra apenas se for
    
    Args:
        new_run_id: ID do run recém treinado
        metric_name: Nome da métrica para comparar
        metric_value: Valor da métrica do novo modelo
    
    Returns:
        True se registrou (ou não precisa), False se erro
    """
    print(f"🔍 evaluate_and_register_if_best chamada:")
    print(f"   new_run_id: {new_run_id[:12]}...")
    print(f"   metric_name: {metric_name}")
    print(f"   metric_value: {metric_value}")
    
    try:
        client = get_client()
        if client is None:
            print(f"❌ Cliente MLflow não disponível")
            return False
        
        # Verificar se há modelo em produção
        print(f"   Verificando modelo em produção...")
        production_version = get_production_model_version()
        print(f"   Versão em produção: {production_version}")
        
        if not production_version:
            # Primeiro modelo - registrar
            print(f"ℹ️  Primeiro modelo - será registrado")
            try:
                model_uri = f"runs:/{new_run_id}/model"
                model_version = mlflow.register_model(model_uri, MODEL_NAME)
                client.set_model_version_tag(
                    name=MODEL_NAME,
                    version=model_version.version,
                    key="is_best",
                    value="true"
                )
                client.set_model_version_tag(
                    name=MODEL_NAME,
                    version=model_version.version,
                    key=metric_name,
                    value=str(metric_value)
                )
                print(f"✅ Primeiro modelo registrado como versão {model_version.version}")
                print(f"   {metric_name}: {metric_value:.4f}")
                return True
            except Exception as e:
                print(f"⚠️  Erro ao registrar primeiro modelo: {e}")
                return False
        
        # Há modelo em produção - comparar
        print(f"   Há modelo em produção - comparando...")
        try:
            prod_version_obj = client.get_model_version(MODEL_NAME, production_version)
            print(f"   Versão em produção obtida: {prod_version_obj.version}")
            print(f"   Source: {prod_version_obj.source}")
            
            # Obter run_id do modelo em produção
            prod_run_id = None
            if "runs:/" in prod_version_obj.source:
                prod_run_id = prod_version_obj.source.split("runs:/")[1].split("/")[0]
            elif prod_version_obj.run_id:
                # Usar run_id diretamente se disponível
                prod_run_id = prod_version_obj.run_id
            
            if prod_run_id:
                
                # Se é o mesmo run, não fazer nada
                print(f"   Run ID em produção: {prod_run_id[:12]}...")
                
                if prod_run_id == new_run_id:
                    print(f"ℹ️  Modelo recém treinado já está registrado como versão {production_version}")
                    return True
                
                print(f"   Obtendo métricas do run em produção...")
                prod_run = client.get_run(prod_run_id)
                prod_metric = prod_run.data.metrics.get(metric_name, 0.0)
                print(f"   Métrica em produção ({metric_name}): {prod_metric}")
                
                # Converter para float
                if hasattr(prod_metric, 'value'):
                    prod_metric_val = float(prod_metric.value)
                else:
                    prod_metric_val = float(prod_metric)
                
                # Comparar - considerar AUC em caso de empate
                is_better = False
                reason = ""
                
                if metric_value > prod_metric_val:
                    is_better = True
                    reason = f"Precision melhor ({metric_value:.4f} > {prod_metric_val:.4f})"
                elif metric_value == prod_metric_val:
                    # Empate na precision - desempatar por AUC
                    new_run = client.get_run(new_run_id)
                    new_auc = new_run.data.metrics.get("test_auc", 0.0)
                    prod_auc = prod_run.data.metrics.get("test_auc", 0.0)
                    
                    # Converter para float
                    if hasattr(new_auc, 'value'):
                        new_auc_val = float(new_auc.value)
                    else:
                        new_auc_val = float(new_auc)
                    
                    if hasattr(prod_auc, 'value'):
                        prod_auc_val = float(prod_auc.value)
                    else:
                        prod_auc_val = float(prod_auc)
                    
                    if new_auc_val > prod_auc_val:
                        is_better = True
                        reason = f"Precision igual ({metric_value:.4f}), mas AUC melhor ({new_auc_val:.4f} > {prod_auc_val:.4f})"
                    else:
                        reason = f"Precision igual ({metric_value:.4f}), mas AUC pior ou igual ({new_auc_val:.4f} <= {prod_auc_val:.4f})"
                else:
                    reason = f"Precision pior ({metric_value:.4f} < {prod_metric_val:.4f})"
                
                if is_better:
                    # Novo modelo é melhor!
                    print(f"✅ Novo modelo é MELHOR!")
                    print(f"   {reason}")
                    try:
                        model_uri = f"runs:/{new_run_id}/model"
                        model_version = mlflow.register_model(model_uri, MODEL_NAME)
                        
                        # Remover tag is_best da versão anterior
                        try:
                            client.delete_model_version_tag(
                                name=MODEL_NAME,
                                version=production_version,
                                key="is_best"
                            )
                        except:
                            pass
                        
                        # Adicionar tag is_best ao novo
                        client.set_model_version_tag(
                            name=MODEL_NAME,
                            version=model_version.version,
                            key="is_best",
                            value="true"
                        )
                        client.set_model_version_tag(
                            name=MODEL_NAME,
                            version=model_version.version,
                            key=metric_name,
                            value=str(metric_value)
                        )
                        
                        print(f"   Registrado como versão {model_version.version}")
                        print(f"   Versão anterior ({production_version}) não é mais a melhor")
                        return True
                    except Exception as e:
                        print(f"⚠️  Erro ao registrar novo melhor modelo: {e}")
                        return False
                else:
                    # Modelo atual é melhor ou igual
                    print(f"ℹ️  Modelo em produção é melhor ou igual")
                    print(f"   {reason}")
                    print(f"   Novo modelo NÃO será registrado")
                    print(f"   Run salvo para comparação futura")
                    return True
            else:
                # Source não tem formato esperado
                print(f"⚠️  Não foi possível extrair run_id do source: {prod_version_obj.source}")
                print(f"   Registrando novo modelo sem comparação")
                # Registrar novo modelo
                try:
                    model_uri = f"runs:/{new_run_id}/model"
                    model_version = mlflow.register_model(model_uri, MODEL_NAME)
                    client.set_model_version_tag(
                        name=MODEL_NAME,
                        version=model_version.version,
                        key="is_best",
                        value="true"
                    )
                    print(f"✅ Modelo registrado como versão {model_version.version}")
                    return True
                except Exception as e:
                    print(f"⚠️  Erro ao registrar: {e}")
                    return False
        except Exception as e:
            print(f"⚠️  Erro ao comparar com produção: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return False
    
    except Exception as e:
        print(f"⚠️  Erro ao avaliar modelo: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False


def mark_best_as_production(metric_name: str = "test_precision_at_10", force: bool = False) -> bool:
    """
    Seleciona o melhor modelo de TODOS os runs e registra apenas ele no Model Registry
    
    Estratégia: Não cria versão para cada treino, apenas registra o melhor modelo
    como uma única versão em produção, atualizando quando um melhor for encontrado.
    
    Args:
        metric_name: Métrica usada para comparar
        force: Se True, força atualização mesmo se já houver Production
    
    Returns:
        True se sucesso, False caso contrário
    """
    try:
        client = get_client()
        if client is None:
            return False
        
        # Encontrar melhor modelo de TODOS os runs
        best_result = find_best_model_by_metrics(metric_name)
        if not best_result:
            print("⚠️  Nenhum modelo válido encontrado para marcar como Production")
            return False
        
        best_run_id, best_info = best_result
        
        print(f"🔍 Melhor modelo de todos os runs: Run {best_run_id[:8]}... ({metric_name}={best_info['metric_value']:.4f})")
        
        # Verificar se o melhor modelo já está registrado
        model_versions = list(client.search_model_versions(f"name='{MODEL_NAME}'"))
        best_version = None
        
        for version in model_versions:
            if "runs:/" in version.source:
                version_run_id = version.source.split("runs:/")[1].split("/")[0]
                if version_run_id == best_run_id:
                    best_version = version
                    break
        
        # Se o melhor modelo JÁ está registrado, apenas garantir que tem a tag is_best
        if best_version:
            print(f"ℹ️  Melhor modelo já está registrado como versão {best_version.version}")
            
            # Verificar se já tem a tag is_best
            try:
                if isinstance(best_version.tags, dict):
                    tags = best_version.tags
                else:
                    tags = {tag.key: tag.value for tag in best_version.tags} if best_version.tags else {}
            except:
                tags = {}
            
            if tags.get("is_best") == "true":
                print(f"   Tag 'is_best' já está configurada")
                print(f"   Nenhuma mudança necessária")
                return True
            else:
                # Adicionar tag is_best
                try:
                    client.set_model_version_tag(
                        name=MODEL_NAME,
                        version=best_version.version,
                        key="is_best",
                        value="true"
                    )
                    print(f"   Tag 'is_best' adicionada à versão {best_version.version}")
                    
                    # Remover tag de outras versões
                    for version in model_versions:
                        if version.version != best_version.version:
                            try:
                                client.delete_model_version_tag(
                                    name=MODEL_NAME,
                                    version=version.version,
                                    key="is_best"
                                )
                            except:
                                pass
                    
                    return True
                except Exception as e:
                    print(f"⚠️  Erro ao adicionar tag: {e}")
                    return True
        
        # Se chegou aqui, o melhor modelo NÃO está registrado
        # Verificar se há modelo em produção para comparar
        production_version = get_production_model_version()
        
        if production_version and not force:
            try:
                prod_version_obj = client.get_model_version(MODEL_NAME, production_version)
                if "runs:/" in prod_version_obj.source:
                    prod_run_id = prod_version_obj.source.split("runs:/")[1].split("/")[0]
                    
                    # Se o melhor run é o mesmo que está em produção, não registrar novamente
                    if prod_run_id == best_run_id:
                        print(f"ℹ️  Melhor modelo já está em produção (versão {production_version})")
                        print(f"   Nenhuma mudança necessária")
                        return True
                    
                    prod_run = client.get_run(prod_run_id)
                    prod_metric = prod_run.data.metrics.get(metric_name, 0.0)
                    
                    # Converter para float
                    if hasattr(prod_metric, 'value'):
                        prod_metric_val = float(prod_metric.value)
                    else:
                        prod_metric_val = float(prod_metric)
                    
                    # COMPARAR ANTES de registrar
                    if best_info["metric_value"] <= prod_metric_val:
                        print(f"ℹ️  Modelo em produção já é melhor ou igual (métrica: {prod_metric_val:.4f} vs {best_info['metric_value']:.4f})")
                        print(f"   Novo modelo NÃO será registrado no Model Registry")
                        return True  # Retorna True mas NÃO registra
            except Exception as e:
                print(f"⚠️  Erro ao comparar com produção: {e}")
        
        # Se chegou aqui, o melhor modelo NÃO está registrado E é melhor que o atual (ou é o primeiro)
        # Apenas agora registrar no Model Registry
        print(f"✅ Registrando novo melhor modelo...")
        try:
            model_uri = f"runs:/{best_run_id}/model"
            model_version = mlflow.register_model(model_uri, MODEL_NAME)
            best_version = model_version
            print(f"✅ Novo melhor modelo registrado como versão {model_version.version}")
        except Exception as e:
            print(f"⚠️  Erro ao registrar melhor modelo: {e}")
            return False
        
        # NÃO usar transition_model_version_stage (deprecated e com bugs)
        # Em vez disso, adicionar aliases e description para identificar o melhor
        try:
            client.set_model_version_tag(
                name=MODEL_NAME,
                version=best_version.version,
                key="is_best",
                value="true"
            )
            client.set_model_version_tag(
                name=MODEL_NAME,
                version=best_version.version,
                key=metric_name,
                value=str(best_info['metric_value'])
            )
            print(f"✅ Melhor modelo registrado!")
            print(f"   Versão: {best_version.version}")
            print(f"   Run ID: {best_run_id[:8]}...")
            print(f"   {metric_name}: {best_info['metric_value']:.4f}")
            if best_info['other_metrics']:
                print(f"   Outras métricas: {best_info['other_metrics']}")
            
            # Remover tag is_best de versões anteriores
            for version in model_versions:
                if version.version != best_version.version:
                    try:
                        client.delete_model_version_tag(
                            name=MODEL_NAME,
                            version=version.version,
                            key="is_best"
                        )
                    except:
                        pass  # Tag pode não existir
            
            return True
        except Exception as e:
            print(f"⚠️  Erro ao marcar tags: {e}")
            print(f"   Melhor modelo identificado: Run {best_run_id[:8]}... ({metric_name}={best_info['metric_value']:.4f})")
            print(f"   Modelo registrado, mas tags não aplicadas")
            return True  # Ainda é sucesso - modelo está registrado
        
    except Exception as e:
        print(f"⚠️  Erro ao marcar melhor modelo como Production: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

