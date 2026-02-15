#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Blueprint/UserWidget.h"
#include "DeployableBaseStub.generated.h"

UCLASS(Blueprintable)
class ADeployableBaseStub : public AActor
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, BlueprintImplementableEvent)
    void Deployable_Interact(AActor* Interactor);

    UFUNCTION(BlueprintCallable, BlueprintImplementableEvent)
    TSubclassOf<UUserWidget> GetWidgetClass();
};