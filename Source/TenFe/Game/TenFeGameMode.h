#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "TenFeGameMode.generated.h"

UCLASS()
class TENFE_API ATenFeGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    ATenFeGameMode();

protected:
    virtual void BeginPlay() override;
};
