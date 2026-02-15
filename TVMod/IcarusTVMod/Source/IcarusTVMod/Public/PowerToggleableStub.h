#pragma once
#include "CoreMinimal.h"
#include "DeployableBaseStub.h"
#include "PowerToggleableStub.generated.h"

UCLASS(Blueprintable)
class APowerToggleableStub : public ADeployableBaseStub
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, BlueprintImplementableEvent)
    void OnDeviceTurnedOn();

    UFUNCTION(BlueprintCallable, BlueprintImplementableEvent)
    void OnDeviceTurnedOff();

    UFUNCTION(BlueprintCallable, BlueprintImplementableEvent)
    void OnDeviceStartRunning();

    UFUNCTION(BlueprintCallable, BlueprintImplementableEvent)
    void OnDeviceStopRunning();
};